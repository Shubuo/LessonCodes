"""
Turkish Stress Detection v2.0 - Training Script
Combines weighted loss, CRF layer, and balanced dataset for improved performance
"""
import os
import sys
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizerFast, get_linear_schedule_with_warmup
from tqdm import tqdm
import numpy as np
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from collections import Counter

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.bert_crf import BertCRF, create_bert_crf_model, CRF_AVAILABLE
from models.weighted_loss import compute_class_weights, WeightedCrossEntropyLoss, FocalLoss
import config


class EmphasisDataset(Dataset):
    """Dataset for emphasis detection with JSONL support"""
    
    def __init__(self, samples, tokenizer, max_length=128):
        self.samples = samples
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.label2id = {"O": 0, "B-EMPHASIS": 1, "I-EMPHASIS": 2}
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Get words and labels
        if isinstance(sample, dict):
            words = sample.get('tokens', sample.get('words', []))
            labels = sample.get('bio_tags', sample.get('labels', []))
        else:
            words = sample.tokens if hasattr(sample, 'tokens') else sample.words
            labels = sample.bio_tags if hasattr(sample, 'bio_tags') else sample.labels
        
        # Convert string labels to ids
        if labels and isinstance(labels[0], str):
            labels = [self.label2id.get(l, 0) for l in labels]
        
        # Tokenize
        encoding = self.tokenizer(
            words,
            is_split_into_words=True,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )
        
        # Align labels with word pieces
        word_ids = encoding.word_ids()
        aligned_labels = []
        previous_word_idx = None
        
        for word_idx in word_ids:
            if word_idx is None:
                aligned_labels.append(-100)  # Special tokens
            elif word_idx != previous_word_idx:
                if word_idx < len(labels):
                    aligned_labels.append(labels[word_idx])
                else:
                    aligned_labels.append(0)
            else:
                # Same word, propagate label
                if word_idx < len(labels):
                    aligned_labels.append(labels[word_idx])
                else:
                    aligned_labels.append(0)
            previous_word_idx = word_idx
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels': torch.tensor(aligned_labels, dtype=torch.long)
        }


def load_data(data_dir):
    """Load train/val/test data"""
    datasets = {}
    
    for split in ['train', 'val', 'test']:
        filepath = os.path.join(data_dir, f'{split}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                datasets[split] = json.load(f)
            print(f"  Loaded {split}: {len(datasets[split])} samples")
    
    return datasets


def count_labels(samples):
    """Count label distribution"""
    counts = Counter()
    for sample in samples:
        labels = sample.get('bio_tags', sample.get('labels', []))
        if labels and isinstance(labels[0], str):
            for label in labels:
                counts[label] += 1
        else:
            for label in labels:
                if label == 0:
                    counts['O'] += 1
                elif label == 1:
                    counts['B-EMPHASIS'] += 1
                elif label == 2:
                    counts['I-EMPHASIS'] += 1
    return counts


def train_epoch(model, dataloader, optimizer, scheduler, device, loss_fn=None):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    
    progress_bar = tqdm(dataloader, desc="Training")
    for batch in progress_bar:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        optimizer.zero_grad()
        
        outputs = model(input_ids, attention_mask, labels)
        loss = outputs['loss']
        
        # Apply custom loss if provided and model doesn't use CRF
        if loss_fn is not None and model.crf is None:
            logits = outputs['logits']
            loss = loss_fn(logits, labels)
        
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        
        total_loss += loss.item()
        progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
    
    return total_loss / len(dataloader)


def evaluate(model, dataloader, device):
    """Evaluate model with seqeval metrics"""
    model.eval()
    
    all_predictions = []
    all_labels = []
    id2label = {0: "O", 1: "B-EMPHASIS", 2: "I-EMPHASIS"}
    
    total_correct = 0
    total_tokens = 0
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels']
            
            # Get predictions
            predictions = model.decode(input_ids, attention_mask)
            
            # Convert to label strings for seqeval
            for pred_seq, label_seq, mask in zip(predictions, labels, attention_mask):
                pred_labels = []
                true_labels = []
                
                # Ensure pred_seq is a list
                if not isinstance(pred_seq, list):
                    pred_seq = pred_seq.tolist() if hasattr(pred_seq, 'tolist') else list(pred_seq)
                
                label_list = label_seq.tolist()
                mask_list = mask.tolist()
                
                for i in range(min(len(pred_seq), len(label_list), len(mask_list))):
                    p = pred_seq[i]
                    l = label_list[i]
                    m = mask_list[i]
                    
                    if m == 1 and l != -100:  # Valid token
                        pred_labels.append(id2label.get(p, "O"))
                        true_labels.append(id2label.get(l, "O"))
                        
                        # Simple accuracy
                        if p == l:
                            total_correct += 1
                        total_tokens += 1
                
                if pred_labels and true_labels:
                    all_predictions.append(pred_labels)
                    all_labels.append(true_labels)
    
    # Calculate simple accuracy
    accuracy = total_correct / total_tokens if total_tokens > 0 else 0
    
    # Calculate metrics using seqeval (with zero_division handling)
    if all_labels and all_predictions:
        try:
            metrics = {
                'accuracy': accuracy,
                'f1': f1_score(all_labels, all_predictions, zero_division=0),
                'precision': precision_score(all_labels, all_predictions, zero_division=0),
                'recall': recall_score(all_labels, all_predictions, zero_division=0),
            }
            report = classification_report(all_labels, all_predictions, zero_division=0)
        except Exception as e:
            print(f"Warning: seqeval error: {e}")
            metrics = {'accuracy': accuracy, 'f1': 0.0, 'precision': 0.0, 'recall': 0.0}
            report = "No valid predictions"
    else:
        metrics = {'accuracy': accuracy, 'f1': 0.0, 'precision': 0.0, 'recall': 0.0}
        report = "No valid predictions"
    
    return metrics, report


def main():
    print("="*60)
    print("Turkish Stress Detection v2.0 - Training")
    print("="*60)
    
    # Configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\nDevice: {device}")
    
    # Hyperparameters
    BATCH_SIZE = 8
    LEARNING_RATE = 2e-5
    NUM_EPOCHS = 5
    WARMUP_RATIO = 0.1
    WEIGHT_DECAY = 0.01
    USE_CRF = CRF_AVAILABLE
    USE_WEIGHTED_LOSS = True
    LOSS_TYPE = "weighted"  # "weighted", "focal", or "standard"
    
    print(f"\nHyperparameters:")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Learning rate: {LEARNING_RATE}")
    print(f"  Epochs: {NUM_EPOCHS}")
    print(f"  CRF: {USE_CRF}")
    print(f"  Loss: {LOSS_TYPE}")
    
    # Load tokenizer
    print("\nLoading tokenizer...")
    tokenizer = BertTokenizerFast.from_pretrained(config.MODEL_CHECKPOINT)
    
    # Load data
    print("\nLoading data...")
    data_dir = config.PROCESSED_DIR
    datasets = load_data(data_dir)
    
    if not datasets:
        print("❌ No data found! Run data_loader.py first.")
        return
    
    # Count labels for class weights
    label_counts = count_labels(datasets.get('train', []))
    print(f"\nLabel distribution:")
    for label, count in label_counts.items():
        print(f"  {label}: {count}")
    
    # Create datasets
    train_dataset = EmphasisDataset(datasets['train'], tokenizer)
    val_dataset = EmphasisDataset(datasets['val'], tokenizer)
    test_dataset = EmphasisDataset(datasets['test'], tokenizer)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)
    
    # Create model
    print("\nCreating model...")
    model = create_bert_crf_model(num_labels=3, model_name=config.MODEL_CHECKPOINT)
    model.to(device)
    
    # Create loss function
    loss_fn = None
    if not USE_CRF and USE_WEIGHTED_LOSS:
        class_counts = [label_counts.get('O', 1), 
                       label_counts.get('B-EMPHASIS', 1), 
                       label_counts.get('I-EMPHASIS', 1)]
        
        if LOSS_TYPE == "weighted":
            loss_fn = WeightedCrossEntropyLoss(class_counts, method="inverse")
        elif LOSS_TYPE == "focal":
            weights = compute_class_weights(class_counts, "inverse").tolist()
            loss_fn = FocalLoss(gamma=2.0, alpha=weights)
        
        if loss_fn:
            loss_fn.to(device) if hasattr(loss_fn, 'to') else None
    
    # Optimizer and scheduler
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    total_steps = len(train_loader) * NUM_EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    scheduler = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)
    
    # Training loop
    print("\n" + "="*60)
    print("Starting training...")
    print("="*60)
    
    best_f1 = 0
    best_epoch = 0
    
    for epoch in range(NUM_EPOCHS):
        print(f"\n--- Epoch {epoch+1}/{NUM_EPOCHS} ---")
        
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, scheduler, device, loss_fn)
        print(f"Train Loss: {train_loss:.4f}")
        
        # Evaluate
        metrics, report = evaluate(model, val_loader, device)
        print(f"Val F1: {metrics['f1']:.4f} | Precision: {metrics['precision']:.4f} | Recall: {metrics['recall']:.4f}")
        
        # Save best model
        if metrics['f1'] > best_f1:
            best_f1 = metrics['f1']
            best_epoch = epoch + 1
            
            # Save model
            save_dir = os.path.join(config.CHECKPOINT_DIR, 'best_model_v2')
            os.makedirs(save_dir, exist_ok=True)
            torch.save(model.state_dict(), os.path.join(save_dir, 'model.pt'))
            tokenizer.save_pretrained(save_dir)
            print(f"  ✓ Saved best model (F1: {best_f1:.4f})")
    
    # Final evaluation on test set
    print("\n" + "="*60)
    print("Final Evaluation on Test Set")
    print("="*60)
    
    # Load best model
    model.load_state_dict(torch.load(os.path.join(save_dir, 'model.pt')))
    test_metrics, test_report = evaluate(model, test_loader, device)
    
    print(f"\nTest Results:")
    print(f"  F1: {test_metrics['f1']:.4f}")
    print(f"  Precision: {test_metrics['precision']:.4f}")
    print(f"  Recall: {test_metrics['recall']:.4f}")
    print(f"\nDetailed Report:\n{test_report}")
    
    # Save results
    results = {
        'best_epoch': best_epoch,
        'best_val_f1': best_f1,
        'test_f1': test_metrics['f1'],
        'test_precision': test_metrics['precision'],
        'test_recall': test_metrics['recall'],
        'config': {
            'batch_size': BATCH_SIZE,
            'learning_rate': LEARNING_RATE,
            'epochs': NUM_EPOCHS,
            'use_crf': USE_CRF,
            'loss_type': LOSS_TYPE
        }
    }
    
    results_path = os.path.join(config.RESULTS_DIR, 'train_v2_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Results saved to {results_path}")


if __name__ == "__main__":
    main()
