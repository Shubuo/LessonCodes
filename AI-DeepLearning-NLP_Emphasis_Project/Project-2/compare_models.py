"""
Generate Section 5 comparison artifacts for baseline vs CRF+SCL models.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import config


OUTPUT_DIR = config.RESULTS_DIR / "comparisons"
BASELINE_PATH = config.RESULTS_DIR / "baseline_ce" / "summary.json"
JOINT_PATH = config.RESULTS_DIR / "train_v2_results.json"


def load_json(path: Path) -> Optional[Dict]:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except Exception:
        header = "| " + " | ".join(df.columns.astype(str)) + " |"
        separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"
        rows = [
            "| "
            + " | ".join("" if pd.isna(value) else str(value) for value in row)
            + " |"
            for row in df.itertuples(index=False, name=None)
        ]
        return "\n".join([header, separator, *rows])


def build_metric_row(model_name: str, payload: Dict, split_name: str) -> Dict:
    split_payload = payload.get(split_name) or {}
    return {
        "model": model_name,
        "split": split_name,
        "weighted_f1": split_payload.get("f1_weighted"),
        "macro_f1": split_payload.get("f1_macro"),
        "precision": split_payload.get("precision"),
        "recall": split_payload.get("recall"),
        "i_emphasis_f1": split_payload.get("minority_i_emphasis_f1"),
        "i_emphasis_recall": split_payload.get("minority_i_emphasis_recall"),
    }


def flatten_comparison_rows(baseline: Dict, joint: Dict) -> List[Dict]:
    rows = []
    for model_name, payload in [
        ("Baseline CE", baseline),
        ("BERT+CRF+SCL", joint),
    ]:
        if not payload:
            continue
        for split_name in ["test", "ood"]:
            if payload.get(split_name) is not None:
                rows.append(build_metric_row(model_name, payload, split_name))
    return rows


def build_hyperparameter_rows(baseline: Dict, joint: Dict) -> List[Dict]:
    rows = []
    if baseline:
        cfg = baseline.get("config", {})
        rows.append(
            {
                "model": "Baseline CE",
                "dropout": cfg.get("dropout"),
                "encoder_lr": cfg.get("learning_rate"),
                "head_lr": cfg.get("learning_rate"),
                "scl_weight": 0.0,
                "epochs": cfg.get("epochs"),
                "batch_size": cfg.get("batch_size"),
                "notes": "Library token classification head + cross-entropy",
            }
        )
    if joint:
        cfg = joint.get("config", {})
        rows.append(
            {
                "model": "BERT+CRF+SCL",
                "dropout": cfg.get("dropout"),
                "encoder_lr": cfg.get("encoder_lr"),
                "head_lr": cfg.get("head_lr"),
                "scl_weight": cfg.get("scl_weight"),
                "epochs": cfg.get("epochs"),
                "batch_size": cfg.get("batch_size"),
                "notes": "Custom CRF decoder + custom CLS supervised contrastive loss",
            }
        )
    return rows


def save_metric_table(rows: List[Dict], output_dir: Path) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "model_comparison.csv"
    df.to_csv(csv_path, index=False)

    pretty_df = df.copy()
    metric_columns = [
        "weighted_f1",
        "macro_f1",
        "precision",
        "recall",
        "i_emphasis_f1",
        "i_emphasis_recall",
    ]
    for column in metric_columns:
        if column in pretty_df:
            pretty_df[column] = pretty_df[column].map(
                lambda value: round(value, 4) if pd.notnull(value) else value
            )

    md_path = output_dir / "model_comparison.md"
    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write("# Model Comparison\n\n")
        handle.write(dataframe_to_markdown(pretty_df))
        handle.write("\n")

    return df


def save_hyperparameter_table(rows: List[Dict], output_dir: Path) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    csv_path = output_dir / "hyperparameter_comparison.csv"
    df.to_csv(csv_path, index=False)

    md_path = output_dir / "hyperparameter_comparison.md"
    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write("# Hyperparameter Comparison\n\n")
        handle.write(dataframe_to_markdown(df))
        handle.write("\n")

    return df


def save_comparison_plot(df: pd.DataFrame, output_dir: Path):
    if df.empty:
        return

    plot_df = df[df["split"] == "test"].copy()
    if plot_df.empty:
        return

    metric_order = ["weighted_f1", "i_emphasis_f1", "i_emphasis_recall"]
    melt_df = plot_df.melt(
        id_vars=["model"],
        value_vars=metric_order,
        var_name="metric",
        value_name="score",
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(data=melt_df, x="metric", y="score", hue="model")
    plt.ylim(0, 1)
    plt.title("Section 5 Comparison on Test Split")
    plt.xlabel("Metric")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.savefig(output_dir / "model_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()


def save_method_note(output_dir: Path):
    note = """# Code Origin Note

## Library-Provided Components

- Hugging Face Transformers backbone loading and tokenizers
- `AutoModelForTokenClassification` baseline head
- `torchcrf` CRF implementation
- `sklearn` metrics and confusion matrices
- `matplotlib` / `seaborn` plotting

## Custom-Written Components

- CLS-based supervised contrastive loss in `models/bert_crf.py`
- Projection head and joint loss fusion logic
- Contrastive label derivation and hybrid OOD data preparation in `data_loader.py`
- Separate CRF+SCL and baseline training pipelines with minority-class reporting
- Comparison artifact generation in `compare_models.py`
"""
    with open(output_dir / "code_origin.md", "w", encoding="utf-8") as handle:
        handle.write(note)


def main():
    baseline = load_json(BASELINE_PATH)
    joint = load_json(JOINT_PATH)

    if baseline is None and joint is None:
        raise FileNotFoundError("No baseline or joint-model result files were found.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metric_rows = flatten_comparison_rows(baseline, joint)
    metric_df = save_metric_table(metric_rows, OUTPUT_DIR)
    hyper_df = save_hyperparameter_table(
        build_hyperparameter_rows(baseline, joint), OUTPUT_DIR
    )
    save_comparison_plot(metric_df, OUTPUT_DIR)
    save_method_note(OUTPUT_DIR)

    summary = {
        "comparison_rows": len(metric_df),
        "hyperparameter_rows": len(hyper_df),
        "artifacts": [
            "model_comparison.csv",
            "model_comparison.md",
            "model_comparison.png",
            "hyperparameter_comparison.csv",
            "hyperparameter_comparison.md",
            "code_origin.md",
        ],
    }
    with open(OUTPUT_DIR / "summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print(f"✓ Comparison artifacts saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
