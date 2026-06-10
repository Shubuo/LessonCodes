"""
BERT-style encoder + CRF model with CLS-based supervised contrastive loss.
"""

from typing import List, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel

try:
    from torchcrf import CRF

    CRF_AVAILABLE = True
except ImportError:
    CRF_AVAILABLE = False
    print("⚠️ torchcrf not installed. Run: pip install pytorch-crf")


class BertCRF(nn.Module):
    """Token classifier with an optional CRF decoder and CLS contrastive head."""

    def __init__(
        self,
        model_name: str = "dbmdz/bert-base-turkish-cased",
        num_labels: int = 3,
        dropout: float = 0.1,
        projection_hidden_dim: int = 256,
        projection_dim: int = 128,
        scl_temperature: float = 0.07,
        contrastive_loss_weight: float = 0.2,
        trust_remote_code: bool = False,
    ):
        super().__init__()

        self.num_labels = num_labels
        self.scl_temperature = scl_temperature
        self.contrastive_loss_weight = contrastive_loss_weight
        self.label2id = {"O": 0, "B-EMPHASIS": 1, "I-EMPHASIS": 2}
        self.id2label = {v: k for k, v in self.label2id.items()}

        # Encoder is the contextual backbone. It produces one hidden vector per token.
        self.encoder = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=trust_remote_code,
        )
        self.hidden_size = self.encoder.config.hidden_size

        self.dropout = nn.Dropout(dropout)
        # This linear layer maps each contextual token vector to BIO label emissions.
        self.classifier = nn.Linear(self.hidden_size, num_labels)
        # Projection head is only used by the supervised contrastive branch.
        # We project the CLS embedding into a smaller space before computing similarity.
        self.projection_head = nn.Sequential(
            nn.Linear(self.hidden_size, projection_hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(projection_hidden_dim, projection_dim),
        )

        if CRF_AVAILABLE:
            self.crf = CRF(num_tags=num_labels, batch_first=True)
            self._init_crf_transitions()
        else:
            self.crf = None
            print("⚠️ CRF not available, using standard classification")

    def _init_crf_transitions(self):
        """Seed the CRF with BIO-consistent transition priors."""
        if self.crf is None:
            return

        with torch.no_grad():
            # I-EMPHASIS should not start a sequence without a preceding emphasis span.
            self.crf.transitions[0, 2] = -10.0
            self.crf.start_transitions[2] = -10.0
            # Encourage continuing an emphasis span once it has started.
            self.crf.transitions[1, 2] = 2.0
            self.crf.transitions[2, 2] = 1.0

    @staticmethod
    def _zero_loss(reference_tensor: torch.Tensor) -> torch.Tensor:
        return reference_tensor.new_tensor(0.0)

    def compute_supervised_contrastive_loss(
        self,
        embeddings: torch.Tensor,
        contrastive_labels: Optional[torch.Tensor],
    ) -> torch.Tensor:
        """Compute supervised contrastive loss over normalized CLS embeddings."""
        if contrastive_labels is None or embeddings.size(0) < 2:
            return self._zero_loss(embeddings)

        # Remove rows that do not have a valid sentence-level contrastive label.
        valid_mask = contrastive_labels.ge(0)
        embeddings = embeddings[valid_mask]
        labels = contrastive_labels[valid_mask]

        if embeddings.size(0) < 2:
            return self._zero_loss(embeddings)

        # Normalize features so cosine-style similarity is controlled by direction.
        features = F.normalize(embeddings, p=2, dim=-1)
        logits = torch.matmul(features, features.T) / self.scl_temperature
        logits = logits - logits.max(dim=1, keepdim=True).values.detach()

        batch_size = labels.size(0)
        device = labels.device
        logits_mask = torch.ones((batch_size, batch_size), device=device)
        logits_mask.fill_diagonal_(0.0)

        # Positive pairs are sentences that share the same coarse emphasis label.
        positive_mask = (
            labels.unsqueeze(0).eq(labels.unsqueeze(1)).float() * logits_mask
        )
        positive_counts = positive_mask.sum(dim=1)
        valid_rows = positive_counts > 0

        if not valid_rows.any():
            return self._zero_loss(features)

        # Standard supervised contrastive objective:
        # pull same-label examples together, push others apart.
        exp_logits = torch.exp(logits) * logits_mask
        log_prob = logits - torch.log(exp_logits.sum(dim=1, keepdim=True) + 1e-12)
        mean_log_prob_pos = (positive_mask * log_prob).sum(
            dim=1
        ) / positive_counts.clamp_min(1.0)

        return -mean_log_prob_pos[valid_rows].mean()

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
        contrastive_labels: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
    ) -> dict:
        """Run the encoder, token classifier, and optional joint losses."""
        encoder_kwargs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }
        if token_type_ids is not None:
            encoder_kwargs["token_type_ids"] = token_type_ids

        outputs = self.encoder(**encoder_kwargs)
        sequence_output = self.dropout(outputs.last_hidden_state)
        # CLS is used as a sentence summary for the contrastive branch.
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        contrastive_embedding = self.projection_head(cls_embedding)
        # Emissions are per-token raw scores before CRF decoding.
        emissions = self.classifier(sequence_output)

        result = {
            "logits": emissions,
            "cls_embedding": cls_embedding,
            "contrastive_embedding": contrastive_embedding,
        }

        scl_loss = self.compute_supervised_contrastive_loss(
            contrastive_embedding,
            contrastive_labels,
        )
        result["scl_loss"] = scl_loss

        if labels is not None:
            if self.crf is not None:
                # torchcrf expects a contiguous mask, so special tokens are trained as O.
                crf_mask = attention_mask.bool()
                labels_crf = labels.clone()
                labels_crf[labels == -100] = self.label2id["O"]
                # CRF returns log-likelihood, so we negate it to obtain a minimization loss.
                crf_loss = -self.crf(
                    emissions, labels_crf, mask=crf_mask, reduction="mean"
                )
            else:
                # Fallback path if torchcrf is unavailable on the environment.
                loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
                crf_loss = loss_fct(
                    emissions.view(-1, self.num_labels), labels.view(-1)
                )

            result["crf_loss"] = crf_loss
            # Final objective jointly optimizes token tagging and sentence-level separation.
            result["loss"] = crf_loss + (self.contrastive_loss_weight * scl_loss)
        elif contrastive_labels is not None:
            result["loss"] = self.contrastive_loss_weight * scl_loss

        return result

    def decode(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        token_type_ids: Optional[torch.Tensor] = None,
    ) -> List[List[int]]:
        """Decode the best BIO path with CRF or argmax fallback."""
        with torch.no_grad():
            encoder_kwargs = {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
            }
            if token_type_ids is not None:
                encoder_kwargs["token_type_ids"] = token_type_ids

            outputs = self.encoder(**encoder_kwargs)
            emissions = self.classifier(self.dropout(outputs.last_hidden_state))

            if self.crf is not None:
                # CRF decoding enforces a globally consistent BIO sequence.
                predictions = self.crf.decode(emissions, mask=attention_mask.bool())
            else:
                # Argmax fallback ignores transition structure but still gives usable predictions.
                predictions = torch.argmax(emissions, dim=-1).tolist()

        return predictions

    def predict(self, tokenizer, text: str, device: str = "cpu") -> dict:
        """Predict emphasis labels for a single sentence."""
        self.eval()
        self.to(device)

        words = text.split()
        # We tokenize at word level first so we can map subword predictions back to words.
        encoding = tokenizer(
            words,
            is_split_into_words=True,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128,
        )

        input_ids = encoding["input_ids"].to(device)
        attention_mask = encoding["attention_mask"].to(device)
        predictions = self.decode(input_ids, attention_mask)
        pred_tags = predictions[0]

        word_ids = encoding.word_ids()
        word_labels = []
        prev_word_idx = None

        for idx, word_idx in enumerate(word_ids):
            # Keep only the first sub-token prediction for each original word.
            if word_idx is not None and word_idx != prev_word_idx:
                if idx < len(pred_tags):
                    word_labels.append(self.id2label[pred_tags[idx]])
                prev_word_idx = word_idx

        highlighted = []
        for word, label in zip(words, word_labels):
            if label in ["B-EMPHASIS", "I-EMPHASIS"]:
                highlighted.append(f"**{word}**")
            else:
                highlighted.append(word)

        return {
            "words": words,
            "labels": word_labels,
            "highlighted": " ".join(highlighted),
        }


def create_bert_crf_model(
    num_labels: int = 3,
    model_name: str = "dbmdz/bert-base-turkish-cased",
    **kwargs,
) -> BertCRF:
    """Create the joint CRF + contrastive model."""
    model = BertCRF(model_name=model_name, num_labels=num_labels, **kwargs)

    # These counts are useful in the demo because they show model scale transparently.
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    print(f"✓ Model created: {model_name}")
    print(f"  Total parameters: {total_params:,}")
    print(f"  Trainable parameters: {trainable_params:,}")
    print(f"  CRF enabled: {model.crf is not None}")
    print(f"  SCL enabled: {model.contrastive_loss_weight > 0}")

    return model


if __name__ == "__main__":
    print("Testing BertCRF Model\n")
    print("=" * 50)

    if not CRF_AVAILABLE:
        print("\n❌ Install torchcrf first: pip install pytorch-crf")
    else:
        print("✓ CRF available")

    print("\nCreating model...")
    model = create_bert_crf_model()

    print("\nTesting forward pass...")
    batch_size, seq_len = 2, 10
    input_ids = torch.randint(0, 30000, (batch_size, seq_len))
    attention_mask = torch.ones(batch_size, seq_len, dtype=torch.long)
    labels = torch.randint(0, 3, (batch_size, seq_len))
    contrastive_labels = torch.tensor([1, 1])

    outputs = model(
        input_ids=input_ids,
        attention_mask=attention_mask,
        labels=labels,
        contrastive_labels=contrastive_labels,
    )

    print(f"Loss: {outputs['loss'].item():.4f}")
    print(f"CRF Loss: {outputs['crf_loss'].item():.4f}")
    print(f"SCL Loss: {outputs['scl_loss'].item():.4f}")
    print(f"Logits shape: {outputs['logits'].shape}")

    print("\nTesting decoding...")
    predictions = model.decode(input_ids, attention_mask)
    print(f"Predictions: {predictions}")
