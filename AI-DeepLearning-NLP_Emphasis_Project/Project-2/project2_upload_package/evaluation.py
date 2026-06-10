"""
Standalone evaluation for the BERT + CRF + SCL emphasis detector.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

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
from transformers import AutoTokenizer

import config
from train_v2 import align_labels_with_tokenizer
from models.bert_crf import create_bert_crf_model


LABEL_NAMES = ["O", "B-EMPHASIS", "I-EMPHASIS"]


class EmphasisEvalDataset(Dataset):
    def __init__(self, samples: List[Dict], tokenizer, max_length: int = 128):
        self.samples = samples
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        item = align_labels_with_tokenizer(
            self.tokenizer,
            sample["words"],
            sample["label_ids"],
            self.max_length,
        )
        return item


def load_split(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_checkpoint_config(checkpoint_dir: Path) -> Dict:
    config_path = checkpoint_dir / "training_config.json"
    if not config_path.exists():
        return {
            "model_name": config.MODEL_CHECKPOINT,
            "trust_remote_code": config.TRUST_REMOTE_CODE,
            "dropout": config.MODEL_DROPOUT,
            "projection_hidden_dim": config.SCL_PROJECTION_HIDDEN_DIM,
            "projection_dim": config.SCL_PROJECTION_DIM,
            "scl_temperature": config.SCL_TEMPERATURE,
            "contrastive_loss_weight": config.SCL_LOSS_WEIGHT,
        }
    with open(config_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def collect_predictions(model, dataloader, device) -> Tuple[List[int], List[int]]:
    true_labels = []
    pred_labels = []
    model.eval()
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
                for pred, gold in zip(pred_seq, label_seq.tolist()):
                    if gold == -100:
                        continue
                    pred_labels.append(pred)
                    true_labels.append(gold)
    return true_labels, pred_labels


def compute_metrics(true_labels: List[int], pred_labels: List[int]) -> Dict:
    report = classification_report(
        true_labels,
        pred_labels,
        labels=list(range(len(LABEL_NAMES))),
        target_names=LABEL_NAMES,
        output_dict=True,
        zero_division=0,
    )
    return {
        "precision": precision_score(
            true_labels, pred_labels, average="weighted", zero_division=0
        ),
        "recall": recall_score(
            true_labels, pred_labels, average="weighted", zero_division=0
        ),
        "f1_weighted": f1_score(
            true_labels, pred_labels, average="weighted", zero_division=0
        ),
        "f1_macro": f1_score(
            true_labels, pred_labels, average="macro", zero_division=0
        ),
        "minority_i_emphasis_f1": report.get("I-EMPHASIS", {}).get("f1-score", 0.0),
        "minority_i_emphasis_recall": report.get("I-EMPHASIS", {}).get("recall", 0.0),
        "report": report,
    }


def save_artifacts(
    true_labels: List[int],
    pred_labels: List[int],
    metrics: Dict,
    output_dir: Path,
    split_name: str,
):
    split_dir = output_dir / split_name
    split_dir.mkdir(parents=True, exist_ok=True)

    matrix = confusion_matrix(
        true_labels, pred_labels, labels=list(range(len(LABEL_NAMES)))
    )
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=LABEL_NAMES,
        yticklabels=LABEL_NAMES,
    )
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title(f"{split_name.upper()} Confusion Matrix")
    plt.tight_layout()
    plt.savefig(split_dir / "confusion_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()

    pd.DataFrame(metrics["report"]).transpose().to_csv(
        split_dir / "per_class_metrics.csv"
    )
    with open(split_dir / "metrics.json", "w", encoding="utf-8") as handle:
        json.dump(
            {key: value for key, value in metrics.items() if key != "report"},
            handle,
            indent=2,
        )


def evaluate_split(
    model, tokenizer, samples: List[Dict], split_name: str, output_dir: Path, device
):
    if not samples:
        return None
    dataset = EmphasisEvalDataset(samples, tokenizer, max_length=config.MAX_LENGTH)
    dataloader = DataLoader(dataset, batch_size=config.BATCH_SIZE)
    true_labels, pred_labels = collect_predictions(model, dataloader, device)
    metrics = compute_metrics(true_labels, pred_labels)
    save_artifacts(true_labels, pred_labels, metrics, output_dir, split_name)
    return metrics


def main():
    checkpoint_dir = config.CHECKPOINTS_DIR / "best_model_v2_scl"
    if not checkpoint_dir.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_dir}")

    checkpoint_cfg = load_checkpoint_config(checkpoint_dir)
    tokenizer = AutoTokenizer.from_pretrained(
        checkpoint_dir,
        trust_remote_code=checkpoint_cfg.get("trust_remote_code", False),
    )
    model = create_bert_crf_model(
        model_name=checkpoint_cfg["model_name"],
        dropout=checkpoint_cfg["dropout"],
        projection_hidden_dim=checkpoint_cfg["projection_hidden_dim"],
        projection_dim=checkpoint_cfg["projection_dim"],
        scl_temperature=checkpoint_cfg["scl_temperature"],
        contrastive_loss_weight=checkpoint_cfg["contrastive_loss_weight"],
        trust_remote_code=checkpoint_cfg.get("trust_remote_code", False),
    )
    device = config.get_torch_device()
    model.load_state_dict(torch.load(checkpoint_dir / "model.pt", map_location=device))
    model.to(device)

    output_dir = config.RESULTS_DIR / "standalone_eval"
    output_dir.mkdir(parents=True, exist_ok=True)

    test_samples = load_split(config.PROCESSED_DIR / "test.json")
    ood_samples = load_split(config.OOD_TEST_PATH)

    print("\nEvaluating test split...")
    test_metrics = evaluate_split(
        model, tokenizer, test_samples, "test", output_dir, device
    )
    print(f"  Test weighted F1: {test_metrics['f1_weighted']:.4f}")
    print(f"  Test I-EMPHASIS recall: {test_metrics['minority_i_emphasis_recall']:.4f}")

    ood_metrics = None
    if ood_samples:
        print("\nEvaluating OOD split...")
        ood_metrics = evaluate_split(
            model, tokenizer, ood_samples, "ood", output_dir, device
        )
        print(f"  OOD weighted F1: {ood_metrics['f1_weighted']:.4f}")
        print(f"  OOD I-EMPHASIS F1: {ood_metrics['minority_i_emphasis_f1']:.4f}")

    summary = {
        "test": {key: value for key, value in test_metrics.items() if key != "report"},
        "ood": {key: value for key, value in ood_metrics.items() if key != "report"}
        if ood_metrics
        else None,
    }
    with open(output_dir / "summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(f"\n✓ Standalone evaluation saved to {output_dir}")


if __name__ == "__main__":
    main()
