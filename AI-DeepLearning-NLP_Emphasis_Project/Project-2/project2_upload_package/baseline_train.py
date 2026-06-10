"""
Legacy cross-entropy baseline for Turkish emphasis detection.
"""

import argparse
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
from torch.utils.data import DataLoader
from tqdm import tqdm
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)

import config
from train_v2 import EmphasisDataset, LABEL_NAMES, count_labels, load_data_splits


def create_optimizer(model, learning_rate: float):
    return torch.optim.AdamW(
        model.parameters(), lr=learning_rate, weight_decay=config.WEIGHT_DECAY
    )


def train_epoch(model, dataloader, optimizer, scheduler, device):
    model.train()
    total_loss = 0.0

    for batch in tqdm(dataloader, desc="Training", leave=False):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        token_type_ids = batch.get("token_type_ids")
        if token_type_ids is not None:
            token_type_ids = token_type_ids.to(device)

        optimizer.zero_grad()
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
            token_type_ids=token_type_ids,
        )
        loss = outputs.loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total_loss += loss.item()

    return {"loss": total_loss / max(len(dataloader), 1)}


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

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids,
            )
            predictions = torch.argmax(outputs.logits, dim=-1).cpu()

            for pred_seq, label_seq in zip(predictions, labels):
                for pred, gold in zip(pred_seq.tolist(), label_seq.tolist()):
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
        "report": report,
        "minority_i_emphasis_f1": report.get("I-EMPHASIS", {}).get("f1-score", 0.0),
        "minority_i_emphasis_recall": report.get("I-EMPHASIS", {}).get("recall", 0.0),
    }


def save_split_artifacts(
    true_labels: List[int],
    pred_labels: List[int],
    metrics: Dict,
    output_dir: Path,
    split_name: str,
):
    split_output_dir = output_dir / split_name
    split_output_dir.mkdir(parents=True, exist_ok=True)

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
    plt.title(f"{split_name.upper()} Confusion Matrix (Baseline CE)")
    plt.tight_layout()
    plt.savefig(split_output_dir / "confusion_matrix.png", dpi=300, bbox_inches="tight")
    plt.close()

    pd.DataFrame(metrics["report"]).transpose().to_csv(
        split_output_dir / "per_class_metrics.csv"
    )
    with open(split_output_dir / "metrics.json", "w", encoding="utf-8") as handle:
        json.dump(
            {key: value for key, value in metrics.items() if key != "report"},
            handle,
            indent=2,
        )


def evaluate_split(
    model, dataloader, device, split_name: str, output_dir: Path
) -> Dict:
    true_labels, pred_labels = collect_predictions(model, dataloader, device)
    metrics = compute_token_metrics(true_labels, pred_labels)
    save_split_artifacts(true_labels, pred_labels, metrics, output_dir, split_name)
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
            dataset, batch_size=batch_size, shuffle=(split_name == "train")
        )
    return dataloaders


def parse_args():
    parser = argparse.ArgumentParser(description="Train legacy cross-entropy baseline")
    parser.add_argument("--model_name", default=config.MODEL_CHECKPOINT)
    parser.add_argument("--epochs", type=int, default=config.NUM_EPOCHS)
    parser.add_argument("--batch_size", type=int, default=config.BATCH_SIZE)
    parser.add_argument("--learning_rate", type=float, default=config.LEARNING_RATE)
    parser.add_argument("--dropout", type=float, default=config.MODEL_DROPOUT)
    parser.add_argument(
        "--trust_remote_code", action="store_true", default=config.TRUST_REMOTE_CODE
    )
    parser.add_argument("--run_name", default="baseline_ce")
    return parser.parse_args()


def main():
    args = parse_args()
    device = config.get_torch_device()

    print("=" * 60)
    print("Turkish Stress Detection Baseline - Cross Entropy")
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

    model = AutoModelForTokenClassification.from_pretrained(
        args.model_name,
        num_labels=config.NUM_LABELS,
        id2label=config.ID2LABEL,
        label2id=config.LABEL2ID,
        hidden_dropout_prob=args.dropout,
        attention_probs_dropout_prob=args.dropout,
        ignore_mismatched_sizes=True,
        trust_remote_code=args.trust_remote_code,
    )
    model.to(device)

    optimizer = create_optimizer(model, learning_rate=args.learning_rate)
    total_steps = len(dataloaders["train"]) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=config.WARMUP_STEPS,
        num_training_steps=total_steps,
    )

    best_val_f1 = -1.0
    save_dir = config.CHECKPOINTS_DIR / args.run_name
    save_dir.mkdir(parents=True, exist_ok=True)
    output_dir = config.RESULTS_DIR / args.run_name
    output_dir.mkdir(parents=True, exist_ok=True)

    history = []
    for epoch in range(args.epochs):
        print(f"\n--- Epoch {epoch + 1}/{args.epochs} ---")
        train_stats = train_epoch(
            model, dataloaders["train"], optimizer, scheduler, device
        )
        print(f"Train Loss: {train_stats['loss']:.4f}")

        val_metrics = evaluate_split(
            model, dataloaders["val"], device, "val", output_dir
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

        if val_metrics["f1_weighted"] > best_val_f1:
            best_val_f1 = val_metrics["f1_weighted"]
            model.save_pretrained(save_dir)
            tokenizer.save_pretrained(save_dir)
            with open(
                save_dir / "training_config.json", "w", encoding="utf-8"
            ) as handle:
                json.dump(
                    {
                        "model_name": args.model_name,
                        "trust_remote_code": args.trust_remote_code,
                        "dropout": args.dropout,
                    },
                    handle,
                    indent=2,
                )
            print(f"  ✓ Saved best baseline model (Val weighted F1: {best_val_f1:.4f})")

    print("\nLoading best checkpoint for final evaluation...")
    model = AutoModelForTokenClassification.from_pretrained(
        save_dir, trust_remote_code=args.trust_remote_code
    )
    model.to(device)

    test_metrics = evaluate_split(
        model, dataloaders["test"], device, "test", output_dir
    )
    print(
        f"Test F1(weighted): {test_metrics['f1_weighted']:.4f} | "
        f"Test I-EMPHASIS Recall: {test_metrics['minority_i_emphasis_recall']:.4f}"
    )

    ood_metrics = None
    if "ood" in dataloaders:
        ood_metrics = evaluate_split(
            model, dataloaders["ood"], device, "ood", output_dir
        )
        print(
            f"OOD F1(weighted): {ood_metrics['f1_weighted']:.4f} | "
            f"OOD I-EMPHASIS F1: {ood_metrics['minority_i_emphasis_f1']:.4f}"
        )

    summary = {
        "model_type": "baseline_cross_entropy",
        "best_val_f1_weighted": best_val_f1,
        "test": {key: value for key, value in test_metrics.items() if key != "report"},
        "ood": {key: value for key, value in ood_metrics.items() if key != "report"}
        if ood_metrics
        else None,
        "history": history,
        "config": {
            "learning_rate": args.learning_rate,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "dropout": args.dropout,
            "model_name": args.model_name,
        },
    }
    with open(output_dir / "summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(f"\n✓ Baseline results saved to {output_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
