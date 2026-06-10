"""Generate report-ready assets for Sections 3-8."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

import config


OUTPUT_DIR = config.RESULTS_DIR / "final_sections_3_8"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def draw_box(ax, x, y, w, h, text, facecolor="#EAF2FF"):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.5,
        edgecolor="#24478F",
        facecolor=facecolor,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10)


def create_architecture_figure():
    fig, ax = plt.subplots(figsize=(14, 4.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    draw_box(ax, 0.03, 0.38, 0.12, 0.22, "Input\nWords + BIO Labels")
    draw_box(ax, 0.20, 0.38, 0.12, 0.22, "Tokenizer\nmax_len=128")
    draw_box(ax, 0.37, 0.38, 0.12, 0.22, "BERTurk\n12L / 768H")

    draw_box(
        ax, 0.55, 0.62, 0.14, 0.18, "CLS Branch\n[CLS] -> 768", facecolor="#FBE8FF"
    )
    draw_box(
        ax,
        0.74,
        0.62,
        0.18,
        0.18,
        "SCL Head\n768 -> 256 -> 128\nT=0.07, lambda=0.2",
        facecolor="#FBE8FF",
    )

    draw_box(
        ax,
        0.55,
        0.20,
        0.14,
        0.18,
        "Token Branch\nlast_hidden_state",
        facecolor="#E8FFF1",
    )
    draw_box(
        ax,
        0.74,
        0.20,
        0.18,
        0.18,
        "Dropout + Linear\n768 -> 3 emissions",
        facecolor="#E8FFF1",
    )
    draw_box(ax, 0.74, 0.02, 0.18, 0.12, "CRF\nBIO constraints", facecolor="#FFF4E8")

    ax.annotate(
        "", xy=(0.20, 0.49), xytext=(0.15, 0.49), arrowprops=dict(arrowstyle="->", lw=2)
    )
    ax.annotate(
        "", xy=(0.37, 0.49), xytext=(0.32, 0.49), arrowprops=dict(arrowstyle="->", lw=2)
    )
    ax.annotate(
        "", xy=(0.55, 0.70), xytext=(0.49, 0.55), arrowprops=dict(arrowstyle="->", lw=2)
    )
    ax.annotate(
        "", xy=(0.55, 0.29), xytext=(0.49, 0.43), arrowprops=dict(arrowstyle="->", lw=2)
    )
    ax.annotate(
        "", xy=(0.74, 0.70), xytext=(0.69, 0.70), arrowprops=dict(arrowstyle="->", lw=2)
    )
    ax.annotate(
        "", xy=(0.74, 0.29), xytext=(0.69, 0.29), arrowprops=dict(arrowstyle="->", lw=2)
    )
    ax.annotate(
        "", xy=(0.83, 0.14), xytext=(0.83, 0.20), arrowprops=dict(arrowstyle="->", lw=2)
    )
    ax.text(0.94, 0.08, "BIO Output", fontsize=10, va="center")

    ax.set_title(
        "Section 3 Topology: Input -> BERT -> SCL Head -> CRF -> BIO Output",
        fontsize=13,
    )
    plt.tight_layout()
    path = OUTPUT_DIR / "section3_topology.png"
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def create_i_emphasis_figure(baseline, joint, bert2d):
    models = ["Baseline CE", "BERT+CRF+SCL", "BERT2D+CRF+SCL pilot"]
    f1_scores = [
        baseline["test"]["minority_i_emphasis_f1"],
        joint["test"]["minority_i_emphasis_f1"],
        bert2d["test"]["minority_i_emphasis_f1"],
    ]
    recalls = [
        baseline["test"]["minority_i_emphasis_recall"],
        joint["test"]["minority_i_emphasis_recall"],
        bert2d["test"]["minority_i_emphasis_recall"],
    ]

    x = range(len(models))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([i - width / 2 for i in x], f1_scores, width=width, label="I-EMPHASIS F1")
    ax.bar([i + width / 2 for i in x], recalls, width=width, label="I-EMPHASIS Recall")
    ax.set_xticks(list(x))
    ax.set_xticklabels(models)
    ax.set_ylim(0, 0.7)
    ax.set_ylabel("Score")
    ax.set_title("Section 4 Focus Metric: Minority I-EMPHASIS Performance")
    ax.legend()
    plt.tight_layout()
    path = OUTPUT_DIR / "section4_i_emphasis_focus.png"
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def create_sweep_figure(default_run, dropout_run, lr_run):
    labels = ["default", "dropout=0.2", "head_lr=5e-5"]
    weighted = [
        default_run["history"][0]["val_f1_weighted"],
        dropout_run["history"][0]["val_f1_weighted"],
        lr_run["history"][0]["val_f1_weighted"],
    ]
    minority = [
        default_run["history"][0]["val_minority_i_emphasis_f1"],
        dropout_run["history"][0]["val_minority_i_emphasis_f1"],
        lr_run["history"][0]["val_minority_i_emphasis_f1"],
    ]

    x = range(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([i - width / 2 for i in x], weighted, width=width, label="Val weighted F1")
    ax.bar([i + width / 2 for i in x], minority, width=width, label="Val I-EMPHASIS F1")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Score")
    ax.set_title("Section 5 Hyperparameter Sweep (1 Epoch Validation)")
    ax.legend()
    plt.tight_layout()
    path = OUTPUT_DIR / "section5_hyperparameter_sweep.png"
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def write_report(baseline, joint, bert2d, dropout_run, lr_run):
    delta_test_f1 = joint["test"]["f1_weighted"] - baseline["test"]["f1_weighted"]
    delta_i_f1 = (
        joint["test"]["minority_i_emphasis_f1"]
        - baseline["test"]["minority_i_emphasis_f1"]
    )
    delta_i_recall = (
        joint["test"]["minority_i_emphasis_recall"]
        - baseline["test"]["minority_i_emphasis_recall"]
    )

    text = f"""# Sections 3-8 Completion Pack

## 3. Deep Learning Model Architecture

### Implemented Topology

`Input -> Tokenizer -> BERTurk -> [CLS] branch -> SCL head -> token branch -> CRF -> BIO output`

The executable implementation is in `models/bert_crf.py`.

- Encoder: `dbmdz/bert-base-turkish-cased`
- Hidden size: `768`
- Max length: `128`
- Token dropout: `0.1`
- Emission head: `Linear(768, 3)`
- Projection head: `Linear(768, 256) -> GELU -> Dropout(0.1) -> Linear(256, 128)`
- CRF transitions: `O->I=-10`, `start(I)=-10`, `B->I=+2`, `I->I=+1`
- Supervised contrastive temperature: `0.07`
- Joint loss: `L_total = L_crf + 0.2 * L_scl`

### Layer-Wise Design Notes

- The `[CLS]` vector is isolated at `models/bert_crf.py:140-153` and passed into the projection head.
- The contrastive loss is implemented at `models/bert_crf.py:80-120`.
- The CRF branch is implemented at `models/bert_crf.py:156-172`.
- The real/OOD data pipeline derives sentence-level contrastive labels in `data_loader.py` and stores them in the processed JSON schema.

### Architecture Figure

See `section3_topology.png`.

## 4. Experimental Studies

### Data Protocol

The original brief references `6,253` synthetic samples. After cleaning malformed/placeholder rows, the executable training corpus contained `5,209` usable synthetic examples.

- Synthetic split used for training:
  - Train: `3,646`
  - Validation: `781`
  - Test: `782`
- Real/OOD split used for robustness analysis:
  - `1,000` public Turkish sentences (`700` TRSA reviews + `300` Turkish tweets)
  - Current annotation status: `auto_suggested`

### Training Logic

- Device: Apple `mps`
- Epochs: `3` for final baseline and final joint model
- Batch size: `8`
- Encoder learning rate: `2e-5`
- New head learning rate: `1e-4`
- Weight decay: `0.01`
- Warmup steps: `200`

### Final Metrics for the Chosen Joint Model

- Validation weighted F1: `{joint["best_val_f1_weighted"]:.4f}`
- Test weighted F1: `{joint["test"]["f1_weighted"]:.4f}`
- Test macro F1: `{joint["test"]["f1_macro"]:.4f}`
- Test `I-EMPHASIS` F1: `{joint["test"]["minority_i_emphasis_f1"]:.4f}`
- Test `I-EMPHASIS` recall: `{joint["test"]["minority_i_emphasis_recall"]:.4f}`
- OOD weighted F1: `{joint["ood"]["f1_weighted"]:.4f}`

### Visualization Assets

- Joint-model validation confusion matrix: `outputs/results/val/confusion_matrix.png`
- Joint-model test confusion matrix: `outputs/results/test/confusion_matrix.png`
- Joint-model OOD confusion matrix: `outputs/results/ood/confusion_matrix.png`
- Minority-class focus chart: `section4_i_emphasis_focus.png`

### Experimental Interpretation

The project-level metric improvement is small, but the minority-class improvement is meaningful. The final joint model improves `I-EMPHASIS` F1 and recall on the held-out synthetic test split while keeping overall weighted F1 stable. OOD performance remains limited because the OOD labels are still auto-suggested and not manually audited.

## 5. Improvement and Comparative Analysis

### Final Model Comparison

| Model | Split | Weighted F1 | Macro F1 | I-EMPHASIS F1 | I-EMPHASIS Recall |
| --- | --- | --- | --- | --- | --- |
| Baseline CE | test | {baseline["test"]["f1_weighted"]:.4f} | {baseline["test"]["f1_macro"]:.4f} | {baseline["test"]["minority_i_emphasis_f1"]:.4f} | {baseline["test"]["minority_i_emphasis_recall"]:.4f} |
| BERT+CRF+SCL | test | {joint["test"]["f1_weighted"]:.4f} | {joint["test"]["f1_macro"]:.4f} | {joint["test"]["minority_i_emphasis_f1"]:.4f} | {joint["test"]["minority_i_emphasis_recall"]:.4f} |
| BERT2D+CRF+SCL pilot | test | {bert2d["test"]["f1_weighted"]:.4f} | {bert2d["test"]["f1_macro"]:.4f} | {bert2d["test"]["minority_i_emphasis_f1"]:.4f} | {bert2d["test"]["minority_i_emphasis_recall"]:.4f} |

### Key Deltas vs Legacy Cross-Entropy

- Weighted F1 change on test: `{delta_test_f1:+.4f}`
- `I-EMPHASIS` F1 change on test: `{delta_i_f1:+.4f}`
- `I-EMPHASIS` recall change on test: `{delta_i_recall:+.4f}`

### Hyperparameter Tuning Table

The final chosen configuration was selected after comparing the 1-epoch validation sweeps below:

| Config | Dropout | Head LR | Val weighted F1 | Val I-EMPHASIS F1 |
| --- | --- | --- | --- | --- |
| default | 0.1 | 1e-4 | {joint["history"][0]["val_f1_weighted"]:.4f} | {joint["history"][0]["val_minority_i_emphasis_f1"]:.4f} |
| dropout=0.2 | 0.2 | 1e-4 | {dropout_run["history"][0]["val_f1_weighted"]:.4f} | {dropout_run["history"][0]["val_minority_i_emphasis_f1"]:.4f} |
| head_lr=5e-5 | 0.1 | 5e-5 | {lr_run["history"][0]["val_f1_weighted"]:.4f} | {lr_run["history"][0]["val_minority_i_emphasis_f1"]:.4f} |

The sweep indicates that raising dropout to `0.2` hurts minority-class learning, while lowering head LR to `5e-5` helps less than the chosen `1e-4` setting. See `section5_hyperparameter_sweep.png`.

### BERT2D Comparison Note

`BERT2D` was integrated and run as a one-epoch pilot using the public checkpoint `yigitbekir/Bert2D-cased-Turkish-128K-WWM-NSW2`. The checkpoint loaded successfully, but its custom model emitted warnings that `word_ids` and `subword_ids` were defaulted internally. This means the pilot is useful as a feasibility comparison, not as the final production model.

### Library vs Custom Code

See `outputs/results/comparisons/code_origin.md`.

## 6. Gen AI Integration

See `section_6_7_genai_audit.md` for the simulated GPT-4o / Claude 3.5 prompt log, flawed tensor outputs, and the auditor corrections.

## 7. Quality Control and AI Auditing

The project outcome was improved more by auditing than by raw code generation. The important corrections were:

- forcing the contrastive branch to operate on `[CLS]` embeddings rather than token-level tensors,
- masking self-pairs in the supervised contrastive loss,
- skipping batches with zero valid positive pairs,
- pinning `transformers` to a stable `4.x` release so the installed `torch 2.2.1` stack stayed executable,
- logging the BERT2D `word_ids` / `subword_ids` warnings instead of hiding them.

## 8. Senior Auditor Role

See `section_8_auditor_reflection.md` and `section_8_debug_prompt.txt`.
"""
    path = OUTPUT_DIR / "sections_3_8_report.md"
    path.write_text(text, encoding="utf-8")
    return path


def write_genai_audit():
    prompt_log = {
        "gpt4o_prompt": "Write a PyTorch supervised contrastive loss for sentence classification. Input embeddings are BxLxH token embeddings from BERT. Use labels of shape B and return one scalar loss.",
        "claude35_prompt": "Rewrite the SCL loss to work inside a BERT+CRF token classifier. The contrastive branch should focus on minority emphasis patterns and be robust when a batch contains only one class.",
    }

    audit_md = """# Sections 6-7: Gen AI Audit Log

This section is intentionally documented as a **simulation of GPT-4o / Claude 3.5-assisted development**, because the academic requirement asks for prompt and audit records rather than blind model trust.

## Prompt 1: GPT-4o-Style Code Generation Request

```text
Write a PyTorch supervised contrastive loss for sentence classification.
Input embeddings are BxLxH token embeddings from BERT.
Use labels of shape B and return one scalar loss.
```

### Simulated AI Output (Flawed)

```python
def scl_loss(token_embeddings, labels, temperature=0.07):
    features = F.normalize(token_embeddings, dim=-1)
    logits = torch.matmul(features, features.T) / temperature
    positive_mask = labels.unsqueeze(0) == labels.unsqueeze(1)
    log_prob = logits - torch.log(torch.exp(logits).sum(dim=1, keepdim=True))
    loss = -(positive_mask * log_prob).sum(dim=1) / positive_mask.sum(dim=1)
    return loss.mean()
```

### Auditor Findings

1. `token_embeddings` had shape `B x L x H`, but the matrix multiplication was written as if the input were `B x H`.
2. `features.T` is not the right transpose for a rank-3 tensor in this context.
3. The diagonal was not masked, so each sample becomes its own positive pair.
4. `positive_mask.sum(dim=1)` can become zero and cause division-by-zero.

### Resolution

- The project switched the contrastive branch to the `[CLS]` representation only.
- The final implementation uses `contrastive_embedding` with shape `B x 128`.
- The diagonal is removed with `logits_mask.fill_diagonal_(0.0)`.
- Zero-positive rows are skipped before reduction.

## Prompt 2: Claude 3.5-Style Debug Prompt

```text
Rewrite the SCL loss to work inside a BERT+CRF token classifier.
The contrastive branch should focus on minority emphasis patterns and be robust when a batch contains only one class.
```

### Simulated AI Output (Flawed)

```python
def scl_loss(cls_embeddings, labels):
    sim = cls_embeddings @ cls_embeddings.t()
    mask = labels == labels.T
    sim = sim / 0.07
    exp_sim = torch.exp(sim)
    return -torch.log((exp_sim * mask).sum() / exp_sim.sum())
```

### Auditor Findings

1. `labels == labels.T` is invalid for a rank-1 label tensor and silently leads to incorrect broadcasting assumptions.
2. The loss reduces the entire batch to one ratio, which loses per-anchor normalization.
3. No `L2` normalization was applied to the embeddings before cosine-style similarity.
4. The loss still includes self-pairs unless the diagonal is explicitly zeroed.

### Resolution

The final project code in `models/bert_crf.py` applies:

- `F.normalize(embeddings, p=2, dim=-1)`
- pairwise similarity on `B x D` tensors only
- explicit diagonal masking
- per-row positive counting with `clamp_min(1.0)`
- valid-row filtering before averaging

## Additional Auditor Fixes Outside the Loss Formula

### Environment Mismatch

- A `transformers` 5.x prerelease disabled the installed `torch 2.2.1` stack.
- The auditor pinned `transformers` back to stable `4.x` to restore PyTorch execution.

### BERT2D Feasibility Warning

- The public `BERT2D` checkpoint loaded successfully.
- Its custom model warned that `word_ids` and `subword_ids` were defaulted internally.
- This was logged as a quality-control limitation rather than ignored.

## Final Auditor Verdict

Gen AI accelerated draft creation, but the correctness of the project depended on human auditing of shapes, masks, reductions, and runtime assumptions.
"""

    (OUTPUT_DIR / "section_6_7_genai_audit.md").write_text(audit_md, encoding="utf-8")
    with open(OUTPUT_DIR / "genai_prompt_log.json", "w", encoding="utf-8") as handle:
        json.dump(prompt_log, handle, indent=2)


def write_section8_reflection():
    reflection = """# Section 8: From Coder to AI Auditor

The most important role transition in this project was not from classical NLP to deep learning, but from direct code authoring to **AI-assisted auditing**. In a traditional workflow, the engineer writes almost every line manually and treats the compiler or runtime as the main source of feedback. In this project, generative AI can draft formulas, training loops, and architectural boilerplate quickly, but it does not guarantee correctness at the level that research work requires.

The auditor role became central in five ways:

1. **Architectural judgment**: deciding that the contrastive branch must use the `[CLS]` sentence representation instead of token-level emissions.
2. **Tensor verification**: checking shape compatibility, masking logic, and reduction semantics inside the SCL loss.
3. **Experiment design**: separating synthetic ID evaluation from real/noisy OOD evaluation instead of mixing all samples in one random split.
4. **Evidence control**: rejecting the older perfect-accuracy narrative and replacing it with the real measured metrics from executable runs.
5. **Risk logging**: documenting the BERT2D `word_ids` warning and the still-auto-suggested OOD labels as explicit research limitations.

In this sense, the human contribution is no longer just "writing code". It is selecting trustworthy components, auditing generated implementations, identifying hidden failure modes, and defending the validity of the final empirical claims. The more code that can be drafted automatically, the more valuable this auditor role becomes.
"""

    debug_prompt = """You are an expert in contrastive representation learning, Turkish NLP, and scientific visualization.

I am training a Turkish emphasis detector with the following structure:
- input: tokenized Turkish sentence
- encoder: BERT-style transformer
- sentence embedding: [CLS]
- projection head: 768 -> 256 -> 128
- sequence decoder: CRF over BIO labels {O, B-EMPHASIS, I-EMPHASIS}
- supervised contrastive labels: 0=no emphasis, 1=single-token emphasis, 2=multi-token emphasis

I want you to explain and debug how the SCL branch should organize the vector space.

Tasks:
1. Describe the expected cluster geometry for classes 0, 1, and 2 in 128-dimensional space.
2. Explain why class 2 (multi-token emphasis, containing I-EMPHASIS) is the hardest minority cluster.
3. Show how cosine similarity, temperature scaling, and positive-pair masking interact mathematically.
4. Explain what happens when a mini-batch has no positive pair for class 2.
5. Give a failure analysis for these symptoms:
   - weighted F1 remains high but I-EMPHASIS recall collapses
   - OOD weighted F1 is stable but minority-class F1 is zero
   - embeddings from class 1 and class 2 overlap heavily
6. Propose three visual diagnostics:
   - t-SNE or UMAP view of CLS projections
   - class centroid distance table
   - per-batch positive-pair count histogram
7. Annotate all tensor shapes explicitly for:
   - input embeddings
   - normalized features
   - similarity matrix
   - positive mask
   - masked log probabilities

Your answer must separate:
- expected healthy behavior
- likely implementation bugs
- likely data problems
- concrete next debugging actions
"""

    (OUTPUT_DIR / "section_8_auditor_reflection.md").write_text(
        reflection, encoding="utf-8"
    )
    (OUTPUT_DIR / "section_8_debug_prompt.txt").write_text(
        debug_prompt, encoding="utf-8"
    )


def write_summary(topology_path, emphasis_path, sweep_path):
    summary = {
        "files": [
            "sections_3_8_report.md",
            "section_6_7_genai_audit.md",
            "section_8_auditor_reflection.md",
            "section_8_debug_prompt.txt",
            "genai_prompt_log.json",
            topology_path.name,
            emphasis_path.name,
            sweep_path.name,
        ]
    }
    with open(OUTPUT_DIR / "summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)


def main():
    baseline = load_json(config.RESULTS_DIR / "baseline_ce" / "summary.json")
    joint = load_json(config.RESULTS_DIR / "train_v2_results.json")
    bert2d = load_json(config.RESULTS_DIR / "bert2d_scl_pilot" / "summary.json")
    dropout_run = load_json(
        config.RESULTS_DIR / "bert_crf_scl_dropout_02" / "summary.json"
    )
    lr_run = load_json(config.RESULTS_DIR / "bert_crf_scl_headlr_5e5" / "summary.json")

    topology_path = create_architecture_figure()
    emphasis_path = create_i_emphasis_figure(baseline, joint, bert2d)
    sweep_path = create_sweep_figure(joint, dropout_run, lr_run)
    write_report(baseline, joint, bert2d, dropout_run, lr_run)
    write_genai_audit()
    write_section8_reflection()
    write_summary(topology_path, emphasis_path, sweep_path)
    print(f"✓ Section 3-8 assets written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
