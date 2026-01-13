"""
BERTurk + CRF Model
Combines BERTurk with Conditional Random Field for sequence labeling
"""
import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizerFast, BertConfig
from typing import Optional, Tuple, List

# Try to import torchcrf, provide installation instructions if not available
try:
    from torchcrf import CRF
    CRF_AVAILABLE = True
except ImportError:
    CRF_AVAILABLE = False
    print("⚠️ torchcrf not installed. Run: pip install pytorch-crf")


class BertCRF(nn.Module):
    """
    BERTurk + CRF for Token Classification
    
    CRF layer learns transition probabilities between tags:
    - P(O → B) should be high
    - P(O → I) should be low (invalid)
    - P(B → I) should be high
    """
    
    def __init__(self, 
                 model_name: str = "dbmdz/bert-base-turkish-cased",
                 num_labels: int = 3,
                 dropout: float = 0.1):
        super().__init__()
        
        self.num_labels = num_labels
        self.label2id = {"O": 0, "B-EMPHASIS": 1, "I-EMPHASIS": 2}
        self.id2label = {v: k for k, v in self.label2id.items()}
        
        # Load BERTurk
        self.bert = BertModel.from_pretrained(model_name)
        self.hidden_size = self.bert.config.hidden_size
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Classification layer
        self.classifier = nn.Linear(self.hidden_size, num_labels)
        
        # CRF layer
        if CRF_AVAILABLE:
            self.crf = CRF(num_tags=num_labels, batch_first=True)
            self._init_crf_transitions()
        else:
            self.crf = None
            print("⚠️ CRF not available, using standard classification")
    
    def _init_crf_transitions(self):
        """
        Initialize CRF transition matrix with prior knowledge:
        - O → I should be penalized (invalid transition)
        - B → I should be encouraged
        """
        if self.crf is None:
            return
        
        # Discourage O → I transition
        # transitions[i,j] = score for transitioning from tag i to tag j
        with torch.no_grad():
            # O=0, B=1, I=2
            # O → I (0 → 2) should be low
            self.crf.transitions[0, 2] = -10.0
            
            # Start with I should be penalized
            self.crf.start_transitions[2] = -10.0
            
            # B → I should be encouraged
            self.crf.transitions[1, 2] = 2.0
            
            # I → I is okay (multi-word emphasis)
            self.crf.transitions[2, 2] = 1.0
    
    def forward(self,
                input_ids: torch.Tensor,
                attention_mask: torch.Tensor,
                labels: Optional[torch.Tensor] = None,
                token_type_ids: Optional[torch.Tensor] = None) -> dict:
        """
        Forward pass
        
        Args:
            input_ids: (batch_size, seq_len)
            attention_mask: (batch_size, seq_len)
            labels: (batch_size, seq_len) - Optional for training
            
        Returns:
            dict with 'loss' and 'logits'
        """
        # BERT encoding
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids
        )
        
        sequence_output = outputs.last_hidden_state
        sequence_output = self.dropout(sequence_output)
        
        # Classification scores
        emissions = self.classifier(sequence_output)
        
        result = {"logits": emissions}
        
        # Compute loss if labels provided
        if labels is not None:
            if self.crf is not None:
                # CRF loss (negative log-likelihood)
                # Mask: 1 for valid tokens, 0 for padding and special tokens
                mask = attention_mask.bool()
                
                # Replace -100 (ignored) labels with 0 for CRF
                labels_crf = labels.clone()
                labels_crf[labels == -100] = 0
                
                # CRF loss
                loss = -self.crf(emissions, labels_crf, mask=mask, reduction='mean')
            else:
                # Standard cross-entropy
                loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
                loss = loss_fct(emissions.view(-1, self.num_labels), labels.view(-1))
            
            result["loss"] = loss
        
        return result
    
    def decode(self, 
               input_ids: torch.Tensor,
               attention_mask: torch.Tensor) -> List[List[int]]:
        """
        Viterbi decoding to get best tag sequence
        
        Returns:
            List of tag sequences (one per batch item)
        """
        with torch.no_grad():
            outputs = self.bert(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            
            sequence_output = outputs.last_hidden_state
            emissions = self.classifier(sequence_output)
            
            if self.crf is not None:
                mask = attention_mask.bool()
                predictions = self.crf.decode(emissions, mask=mask)
            else:
                predictions = torch.argmax(emissions, dim=-1).tolist()
        
        return predictions
    
    def predict(self, 
                tokenizer: BertTokenizerFast,
                text: str,
                device: str = "cpu") -> dict:
        """
        Predict emphasis for a single text
        
        Args:
            tokenizer: BERTurk tokenizer
            text: Input text
            device: Device to run on
            
        Returns:
            dict with words, labels, and highlighted text
        """
        self.eval()
        self.to(device)
        
        # Tokenize
        words = text.split()
        encoding = tokenizer(
            words,
            is_split_into_words=True,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=128
        )
        
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        
        # Decode
        predictions = self.decode(input_ids, attention_mask)
        pred_tags = predictions[0]
        
        # Align predictions with words
        word_ids = encoding.word_ids()
        word_labels = []
        prev_word_idx = None
        
        for idx, word_idx in enumerate(word_ids):
            if word_idx is not None and word_idx != prev_word_idx:
                if idx < len(pred_tags):
                    word_labels.append(self.id2label[pred_tags[idx]])
                prev_word_idx = word_idx
        
        # Create highlighted output
        highlighted = []
        for word, label in zip(words, word_labels):
            if label in ['B-EMPHASIS', 'I-EMPHASIS']:
                highlighted.append(f"**{word}**")
            else:
                highlighted.append(word)
        
        return {
            "words": words,
            "labels": word_labels,
            "highlighted": " ".join(highlighted)
        }


# Model creation helper
def create_bert_crf_model(num_labels: int = 3, 
                          model_name: str = "dbmdz/bert-base-turkish-cased") -> BertCRF:
    """Create BERTurk + CRF model"""
    model = BertCRF(model_name=model_name, num_labels=num_labels)
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"✓ Model created: {model_name}")
    print(f"  Total parameters: {total_params:,}")
    print(f"  Trainable parameters: {trainable_params:,}")
    print(f"  CRF enabled: {model.crf is not None}")
    
    return model


if __name__ == "__main__":
    print("Testing BertCRF Model\n")
    print("="*50)
    
    # Check CRF availability
    if not CRF_AVAILABLE:
        print("\n❌ Install torchcrf first: pip install pytorch-crf")
    else:
        print("✓ CRF available")
    
    # Create model (small test)
    print("\nCreating model...")
    model = create_bert_crf_model()
    
    # Test forward pass
    print("\nTesting forward pass...")
    batch_size, seq_len = 2, 10
    
    input_ids = torch.randint(0, 30000, (batch_size, seq_len))
    attention_mask = torch.ones(batch_size, seq_len, dtype=torch.long)
    labels = torch.randint(0, 3, (batch_size, seq_len))
    labels[0, 0] = -100  # Padding
    
    outputs = model(input_ids, attention_mask, labels)
    
    print(f"Loss: {outputs['loss'].item():.4f}")
    print(f"Logits shape: {outputs['logits'].shape}")
    
    # Test decoding
    print("\nTesting decoding...")
    predictions = model.decode(input_ids, attention_mask)
    print(f"Predictions: {predictions}")
