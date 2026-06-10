"""
Joint training script for BERT/CRF emphasis detection with supervised contrastive loss.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import torch
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm
from transformers import AutoTokenizer, get_linear_schedule_with_warmup

import config
from models.bert_crf import BertCRF, create_bert_crf_model


LABEL_NAMES = ["O", "B-EMPHASIS", "I-EMPHASIS"]


def align_labels_with_tokenizer(
    tokenizer, words: List[str], labels: List[int], max_length: int
):
    """Align word labels to token labels for both fast and slow tokenizers."""
    if getattr(tokenizer, "is_fast", False):
        # Fast tokenizers expose word_ids(), which makes word-to-subword alignment easier.
        encoding = tokenizer(
            words,
            is_split_into_words=True,
            truncation=True,
            max_length=max_length,
            padding="max_length",
            return_tensors="pt",
        )

        word_ids = encoding.word_ids()
        aligned_labels = []
        previous_word_idx = None
        for word_idx in word_ids:
            if word_idx is None:
                # Special tokens such as [CLS], [SEP] and padding should be ignored in loss.
                aligned_labels.append(-100)
            elif word_idx != previous_word_idx:
                # First sub-token keeps the original word label.
                aligned_labels.append(labels[word_idx] if word_idx < len(labels) else 0)
            else:
                # Continuation sub-tokens reuse the same word label in this project setup.
                aligned_labels.append(labels[word_idx] if word_idx < len(labels) else 0)
            previous_word_idx = word_idx

        item = {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(aligned_labels, dtype=torch.long),
        }
        if "token_type_ids" in encoding:
            item["token_type_ids"] = encoding["token_type_ids"].squeeze(0)
        return item

    tokens = []
    aligned_labels = []
    unk_token = tokenizer.unk_token or "[UNK]"
    max_token_length = max_length - tokenizer.num_special_tokens_to_add(pair=False)

    # Slow tokenizers do not provide word_ids(), so we rebuild the mapping manually.
    for word, label in zip(words, labels):
        word_tokens = tokenizer.tokenize(word) or [unk_token]
        for token in word_tokens:
            if len(tokens) >= max_token_length:
                break
            tokens.append(token)
            aligned_labels.append(label)
        if len(tokens) >= max_token_length:
            break

    token_ids = tokenizer.convert_tokens_to_ids(tokens)
    input_ids = tokenizer.build_inputs_with_special_tokens(token_ids)
    token_type_ids = tokenizer.create_token_type_ids_from_sequences(token_ids)
    attention_mask = [1] * len(input_ids)

    if len(input_ids) == len(aligned_labels) + 2:
        label_ids = [-100] + aligned_labels + [-100]
    else:
        # This branch is defensive: some tokenizers may use a different special-token layout.
        prefix_len = 1
        suffix_len = max(len(input_ids) - len(aligned_labels) - prefix_len, 0)
        label_ids = ([-100] * prefix_len) + aligned_labels + ([-100] * suffix_len)
        label_ids = label_ids[: len(input_ids)]

    pad_length = max_length - len(input_ids)
    if pad_length > 0:
        input_ids = input_ids + ([tokenizer.pad_token_id] * pad_length)
        attention_mask = attention_mask + ([0] * pad_length)
        token_type_ids = token_type_ids + ([0] * pad_length)
        label_ids = label_ids + ([-100] * pad_length)

    return {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        "token_type_ids": torch.tensor(token_type_ids, dtype=torch.long),
        "labels": torch.tensor(label_ids, dtype=torch.long),
    }


def derive_contrastive_label(sample: Dict) -> int:
    # Sentence-level contrastive labels are intentionally coarse:
    # 0 = no emphasis, 1 = contains B, 2 = contains I.
    if "contrastive_label" in sample:
        return int(sample["contrastive_label"])
    bio_labels = sample.get("bio_labels", [])
    if "I-EMPHASIS" in bio_labels:
        return 2
    if "B-EMPHASIS" in bio_labels:
        return 1
    return 0


class EmphasisDataset(Dataset):
    """Token classification dataset backed by the processed JSON schema."""

    def __init__(self, samples: List[Dict], tokenizer, max_length: int = 128):
        self.samples = samples
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        words = sample["words"]
        labels = sample["label_ids"]
        contrastive_label = derive_contrastive_label(sample)

        # Each item serves two tasks at once:
        # token-level BIO tagging and sentence-level contrastive grouping.
        item = align_labels_with_tokenizer(
            self.tokenizer, words, labels, self.max_length
        )
        item["contrastive_label"] = torch.tensor(contrastive_label, dtype=torch.long)
        return item


def load_split(file_path: Path) -> List[Dict]:
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_data_splits() -> Dict[str, List[Dict]]:
    # The OOD split is optional, but when present it is evaluated with the same pipeline.
    return {
        "train": load_split(config.PROCESSED_DIR / "train.json"),
        "val": load_split(config.PROCESSED_DIR / "val.json"),
        "test": load_split(config.PROCESSED_DIR / "test.json"),
        "ood": load_split(config.OOD_TEST_PATH),
    }


def count_labels(samples: List[Dict]) -> Dict[str, int]:
    counts = {name: 0 for name in LABEL_NAMES}
    for sample in samples:
        for label_id in sample["label_ids"]:
            counts[LABEL_NAMES[label_id]] += 1
    return counts


def create_optimizer(model: BertCRF, encoder_lr: float, head_lr: float):
    encoder_params = []
    head_params = []
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        if name.startswith("encoder"):
            encoder_params.append(parameter)
        else:
            head_params.append(parameter)

    # We use a lower LR for the pretrained encoder and a higher LR for new task heads.
    optimizer_groups = [
        {"params": encoder_params, "lr": encoder_lr},
        {"params": head_params, "lr": head_lr},
    ]
    return torch.optim.AdamW(optimizer_groups, weight_decay=config.WEIGHT_DECAY)


def train_epoch(model, dataloader, optimizer, scheduler, device):
    model.train()
    running = {"loss": 0.0, "crf_loss": 0.0, "scl_loss": 0.0}

    for batch in tqdm(dataloader, desc="Training", leave=False):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        contrastive_labels = batch["contrastive_label"].to(device)
        token_type_ids = batch.get("token_type_ids")
        if token_type_ids is not None:
            token_type_ids = token_type_ids.to(device)

        optimizer.zero_grad()
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
            contrastive_labels=contrastive_labels,
            token_type_ids=token_type_ids,
        )
        loss = outputs["loss"]
        loss.backward()
        # Gradient clipping helps stabilize training when CRF and contrastive terms interact.
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

        running["loss"] += loss.item()
        running["crf_loss"] += outputs.get("crf_loss", loss).item()
        running["scl_loss"] += outputs.get("scl_loss", loss.new_tensor(0.0)).item()

    num_batches = max(len(dataloader), 1)
    return {key: value / num_batches for key, value in running.items()}


def collect_predictions(model, dataloader, device) -> Tuple[List[int], List[int]]:
    model.eval()
    true_labels: List[int] = []
    pred_labels: List[int] = []

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating", leave=False):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"]
            token_type_ids = batch.get("token_type_ids")
            if token_type_ids is not None:
                token_type_ids = token_type_ids.to(device)

            predictions = model.decode(
                input_ids, attention_mask, token_type_ids=token_type_ids
            )
            for pred_seq, label_seq in zip(predictions, labels):
                label_list = label_seq.tolist()
                for pred, gold in zip(pred_seq, label_list):
                    # Ignore padded/special-token positions so the report reflects real tokens only.
                    if gold == -100:
                        continue
                    pred_labels.append(pred)
                    true_labels.append(gold)

    return true_labels, pred_labels


def compute_token_metrics(true_labels: List[int], pred_labels: List[int]) -> Dict:
    if not true_labels:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1_weighted": 0.0,
            "f1_macro": 0.0,
            "report": {},
        }

    report = classification_report(
        true_labels,
        pred_labels,
        labels=list(range(len(LABEL_NAMES))),
        target_names=LABEL_NAMES,
        output_dict=True,
        zero_division=0,
    )
    return {
        # Weighted F1 reflects overall tagging quality under label imbalance.
        "precision": precision_score(
            true_labels, pred_labels, average="weighted", zero_division=0
        ),
        "recall": recall_score(
            true_labels, pred_labels, average="weighted", zero_division=0
        ),
        "f1_weighted": f1_score(
            true_labels, pred_labels, average="weighted", zero_division=0
        ),
        # Macro F1 is important here because the minority emphasis tags are harder.
        "f1_macro": f1_score(
            true_labels, pred_labels, average="macro", zero_division=0
        ),
        "report": report,
        # We report I-EMPHASIS separately because it is the most fragile minority label.
        "minority_i_emphasis_f1": report.get("I-EMPHASIS", {}).get("f1-score", 0.0),
        "minority_i_emphasis_recall": report.get("I-EMPHASIS", {}).get("recall", 0.0),
    }


def save_confusion_matrix(
    true_labels: List[int], pred_labels: List[int], output_path: Path, title: str
):
    cm = confusion_matrix(
        true_labels, pred_labels, labels=list(range(len(LABEL_NAMES)))
    )
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=LABEL_NAMES,
        yticklabels=LABEL_NAMES,
    )
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def save_report(report: Dict, output_path: Path):
    df = pd.DataFrame(report).transpose()
    df.to_csv(output_path)


def evaluate_split(
    model, dataloader, device, split_name: str, output_dir: Path
) -> Dict:
    true_labels, pred_labels = collect_predictions(model, dataloader, device)
    metrics = compute_token_metrics(true_labels, pred_labels)

    split_output_dir = output_dir / split_name
    split_output_dir.mkdir(parents=True, exist_ok=True)

    # Each split gets its own confusion matrix and per-class CSV so the paper can cite them directly.
    save_confusion_matrix(
        true_labels,
        pred_labels,
        split_output_dir / "confusion_matrix.png",
        title=f"{split_name.upper()} Confusion Matrix",
    )
    save_report(metrics["report"], split_output_dir / "per_class_metrics.csv")
    with open(split_output_dir / "metrics.json", "w", encoding="utf-8") as handle:
        json.dump(
            {key: value for key, value in metrics.items() if key != "report"},
            handle,
            indent=2,
        )

    return metrics


def build_dataloaders(samples: Dict[str, List[Dict]], tokenizer, batch_size: int):
    dataloaders = {}
    for split_name, split_samples in samples.items():
        if not split_samples:
            continue
        dataset = EmphasisDataset(
            split_samples, tokenizer, max_length=config.MAX_LENGTH
        )
        dataloaders[split_name] = DataLoader(
            dataset,
            batch_size=batch_size,
            # Only training is shuffled; eval/test must stay deterministic.
            shuffle=(split_name == "train"),
        )
    return dataloaders


def parse_args():
    parser = argparse.ArgumentParser(description="Train BERT+CRF+SCL emphasis detector")
    parser.add_argument("--model_name", default=config.MODEL_CHECKPOINT)
    parser.add_argument("--epochs", type=int, default=config.NUM_EPOCHS)
    parser.add_argument("--batch_size", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--encoder_lr", type=float, default=config.LEARNING_RATE)
    parser.add_argument("--head_lr", type=float, default=config.HEAD_LEARNING_RATE)
    parser.add_argument("--dropout", type=float, default=config.MODEL_DROPOUT)
    parser.add_argument("--scl_weight", type=float, default=config.SCL_LOSS_WEIGHT)
    parser.add_argument("--temperature", type=float, default=config.SCL_TEMPERATURE)
    parser.add_argument("--projection_dim", type=int, default=config.SCL_PROJECTION_DIM)
    parser.add_argument(
        "--projection_hidden_dim", type=int, default=config.SCL_PROJECTION_HIDDEN_DIM
    )
    parser.add_argument(
        "--trust_remote_code", action="store_true", default=config.TRUST_REMOTE_CODE
    )
    parser.add_argument("--run_name", default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    device = config.get_torch_device()

    print("=" * 60)
    print("Turkish Stress Detection v2.1 - BERT + CRF + SCL")
    print("=" * 60)
    print(f"Device: {device}")

    samples = load_data_splits()
    if not samples["train"] or not samples["val"] or not samples["test"]:
        raise FileNotFoundError(
            "Processed train/val/test splits are missing. Run data_loader.py first."
        )

    print("\nLabel distribution (train):")
    for label_name, count in count_labels(samples["train"]).items():
        print(f"  {label_name}: {count}")

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name, trust_remote_code=args.trust_remote_code
    )
    dataloaders = build_dataloaders(samples, tokenizer, batch_size=args.batch_size)

    # Model combines contextual token representations, CRF decoding, and CLS contrastive learning.
    model = create_bert_crf_model(
        num_labels=config.NUM_LABELS,
        model_name=args.model_name,
        dropout=args.dropout,
        projection_hidden_dim=args.projection_hidden_dim,
        projection_dim=args.projection_dim,
        scl_temperature=args.temperature,
        contrastive_loss_weight=args.scl_weight,
        trust_remote_code=args.trust_remote_code,
    )
    model.to(device)

    optimizer = create_optimizer(
        model, encoder_lr=args.encoder_lr, head_lr=args.head_lr
    )
    total_steps = len(dataloaders["train"]) * args.epochs
    # Linear decay with warmup is a standard safe choice for fine-tuning transformer backbones.
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=config.WARMUP_STEPS,
        num_training_steps=total_steps,
    )

    best_val_f1 = -1.0
    results_dir = (
        config.RESULTS_DIR
        if args.run_name is None
        else (config.RESULTS_DIR / args.run_name)
    )
    results_dir.mkdir(parents=True, exist_ok=True)
    save_dir = config.CHECKPOINTS_DIR / (args.run_name or "best_model_v2_scl")
    save_dir.mkdir(parents=True, exist_ok=True)

    history = []
    for epoch in range(args.epochs):
        print(f"\n--- Epoch {epoch + 1}/{args.epochs} ---")
        train_stats = train_epoch(
            model, dataloaders["train"], optimizer, scheduler, device
        )
        print(
            f"Train Loss: {train_stats['loss']:.4f} | "
            f"CRF: {train_stats['crf_loss']:.4f} | "
            f"SCL: {train_stats['scl_loss']:.4f}"
        )

        val_metrics = evaluate_split(
            model, dataloaders["val"], device, "val", results_dir
        )
        print(
            f"Val F1(weighted): {val_metrics['f1_weighted']:.4f} | "
            f"Val I-EMPHASIS F1: {val_metrics['minority_i_emphasis_f1']:.4f}"
        )
        history.append(
            {
                "epoch": epoch + 1,
                **train_stats,
                **{f"val_{k}": v for k, v in val_metrics.items() if k != "report"},
            }
        )

        # Best checkpoint is selected by validation weighted F1, not by training loss alone.
        if val_metrics["f1_weighted"] > best_val_f1:
            best_val_f1 = val_metrics["f1_weighted"]
            torch.save(model.state_dict(), save_dir / "model.pt")
            tokenizer.save_pretrained(save_dir)
            with open(
                save_dir / "training_config.json", "w", encoding="utf-8"
            ) as handle:
                json.dump(
                    {
                        "model_name": args.model_name,
                        "trust_remote_code": args.trust_remote_code,
                        "dropout": args.dropout,
                        "projection_hidden_dim": args.projection_hidden_dim,
                        "projection_dim": args.projection_dim,
                        "scl_temperature": args.temperature,
                        "contrastive_loss_weight": args.scl_weight,
                    },
                    handle,
                    indent=2,
                )
            print(f"  ✓ Saved best model (Val weighted F1: {best_val_f1:.4f})")

    print("\nLoading best checkpoint for final evaluation...")
    model.load_state_dict(torch.load(save_dir / "model.pt", map_location=device))

    # Final test metrics represent the in-domain result reported in the paper.
    test_metrics = evaluate_split(
        model, dataloaders["test"], device, "test", results_dir
    )
    print(
        f"Test F1(weighted): {test_metrics['f1_weighted']:.4f} | "
        f"Test I-EMPHASIS Recall: {test_metrics['minority_i_emphasis_recall']:.4f}"
    )

    ood_metrics = None
    if "ood" in dataloaders:
        # OOD evaluation checks how brittle the model is outside the main distribution.
        ood_metrics = evaluate_split(
            model, dataloaders["ood"], device, "ood", results_dir
        )
        print(
            f"OOD F1(weighted): {ood_metrics['f1_weighted']:.4f} | "
            f"OOD I-EMPHASIS F1: {ood_metrics['minority_i_emphasis_f1']:.4f}"
        )

    summary = {
        "model_type": "bert_crf_scl",
        "best_val_f1_weighted": best_val_f1,
        "test": {key: value for key, value in test_metrics.items() if key != "report"},
        "ood": {key: value for key, value in ood_metrics.items() if key != "report"}
        if ood_metrics
        else None,
        "history": history,
        "config": {
            "encoder_lr": args.encoder_lr,
            "head_lr": args.head_lr,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "dropout": args.dropout,
            "scl_weight": args.scl_weight,
            "temperature": args.temperature,
            "projection_dim": args.projection_dim,
            "projection_hidden_dim": args.projection_hidden_dim,
            "model_name": args.model_name,
        },
    }
    summary_path = (
        config.RESULTS_DIR / "train_v2_results.json"
        if args.run_name is None
        else (results_dir / "summary.json")
    )
    # This summary file is later consumed by compare_models.py and the report assets.
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(f"\n✓ Results saved to {summary_path}")


if __name__ == "__main__":
    main()
