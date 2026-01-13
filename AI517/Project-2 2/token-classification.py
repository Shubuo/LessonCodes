import torch
from transformers import BertTokenizerFast, BertForTokenClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset

# Türkçe için en iyi performansı veren modellerden biri
MODEL_CHECKPOINT = "dbmdz/bert-base-turkish-cased"

class EmphasisTaggingDataset(Dataset):
    def __init__(self, texts, tags, tokenizer, max_len=128):
        self.texts = texts
        self.tags = tags # Örn:  (1: Vurgulu)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        word_tags = self.tags[idx]
        
        # Tokenizasyon (Offset mapping ile kelime-token hizalaması)
        encoding = self.tokenizer(
            text,
            is_split_into_words=True,
            return_offsets_mapping=True,
            padding='max_length',
            truncation=True,
            max_length=self.max_len
        )
        
        labels = []
        word_ids = encoding.word_ids()
        
        # Kelime etiketlerini token etiketlerine yayma (Label Propagation)
        # Örn: "gideceğim" (Vurgulu) -> ["gid", "##ece", "##ğim"] -> [1, 1, 1]
        previous_word_idx = None
        for word_idx in word_ids:
            if word_idx is None:
                labels.append(-100) # Özel tokenları yoksay
            elif word_idx!= previous_word_idx:
                labels.append(word_tags[word_idx])
            else:
                # Alt tokenlar da ana kelimenin vurgusunu taşır
                labels.append(word_tags[word_idx]) 
            previous_word_idx = word_idx

        item = {key: torch.as_tensor(val) for key, val in encoding.items()}
        item['labels'] = torch.as_tensor(labels)
        del item['offset_mapping'] # Eğitimde gerekmez
        return item


# ==================== DATA LOADING ====================

def load_processed_data(split='train'):
    """Load processed data from JSON files"""
    import json
    from pathlib import Path
    import config
    
    data_path = config.PROCESSED_DIR / f"{split}.json"
    
    if not data_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {data_path}\n"
            f"Please run 'python data_loader.py' first to process the legacy datasets."
        )
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

def prepare_datasets():
    """Prepare train, val, test datasets"""
    import config
    
    tokenizer = BertTokenizerFast.from_pretrained(MODEL_CHECKPOINT)
    
    train_data = load_processed_data('train')
    val_data = load_processed_data('val')
    test_data = load_processed_data('test')
    
    # Extract texts and tags
    train_texts = [ex['words'] for ex in train_data]
    train_tags = [ex['label_ids'] for ex in train_data]
    
    val_texts = [ex['words'] for ex in val_data]
    val_tags = [ex['label_ids'] for ex in val_data]
    
    test_texts = [ex['words'] for ex in test_data]
    test_tags = [ex['label_ids'] for ex in test_data]
    
    # Create datasets
    train_dataset = EmphasisTaggingDataset(train_texts, train_tags, tokenizer)
    val_dataset = EmphasisTaggingDataset(val_texts, val_tags, tokenizer)
    test_dataset = EmphasisTaggingDataset(test_texts, test_tags, tokenizer)
    
    print(f"✓ Loaded datasets:")
    print(f"  Train: {len(train_dataset)} examples")
    print(f"  Val: {len(val_dataset)} examples")
    print(f"  Test: {len(test_dataset)} examples")
    
    return train_dataset, val_dataset, test_dataset, tokenizer


# ==================== EVALUATION METRICS ====================

def compute_metrics(eval_pred):
    """Compute F1, precision, recall for evaluation"""
    from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
    import numpy as np
    import config
    
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=2)
    
    # Flatten and remove ignored index (padding)
    true_labels = []
    pred_labels = []
    
    for pred_seq, label_seq in zip(predictions, labels):
        for pred, label in zip(pred_seq, label_seq):
            if label != -100:  # Ignore padding
                true_labels.append(label)
                pred_labels.append(pred)
    
    # Calculate metrics
    accuracy = accuracy_score(true_labels, pred_labels)
    precision = precision_score(true_labels, pred_labels, average='weighted', zero_division=0)
    recall = recall_score(true_labels, pred_labels, average='weighted', zero_division=0)
    f1 = f1_score(true_labels, pred_labels, average='weighted', zero_division=0)
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }


# ==================== TRAINING ====================

def train_model(output_dir='./outputs/checkpoints'):
    """Train the token classification model"""
    import config
    from transformers import DataCollatorForTokenClassification
    
    print("\n" + "="*60)
    print("🚀 STARTING MODEL TRAINING")
    print("="*60)
    
    # Prepare datasets
    train_dataset, val_dataset, test_dataset, tokenizer = prepare_datasets()
    
    # Initialize model
    model = BertForTokenClassification.from_pretrained(
        MODEL_CHECKPOINT,
        num_labels=config.NUM_LABELS,
        id2label=config.ID2LABEL,
        label2id=config.LABEL2ID
    )
    
    print(f"\n✓ Model initialized: {MODEL_CHECKPOINT}")
    print(f"  Num labels: {config.NUM_LABELS}")
    print(f"  Labels: {list(config.LABEL2ID.keys())}")
    
    # Data collator
    data_collator = DataCollatorForTokenClassification(tokenizer)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        eval_strategy=config.EVALUATION_STRATEGY,  # Changed from evaluation_strategy
        save_strategy=config.SAVE_STRATEGY,
        learning_rate=config.LEARNING_RATE,
        per_device_train_batch_size=config.BATCH_SIZE,
        per_device_eval_batch_size=config.BATCH_SIZE,
        num_train_epochs=config.NUM_EPOCHS,
        weight_decay=config.WEIGHT_DECAY,
        warmup_steps=config.WARMUP_STEPS,
        logging_dir=config.LOGGING_DIR,
        logging_steps=config.LOGGING_STEPS,
        load_best_model_at_end=config.LOAD_BEST_MODEL_AT_END,
        metric_for_best_model=config.METRIC_FOR_BEST_MODEL,
        greater_is_better=config.GREATER_IS_BETTER,
        fp16=config.FP16 and torch.cuda.is_available(),
        gradient_accumulation_steps=config.GRADIENT_ACCUMULATION_STEPS,
        save_total_limit=3,
        report_to="none",  # Disable wandb/tensorboard to avoid dependencies
    )
    
    print(f"\n✓ Training configuration:")
    print(f"  Batch size: {config.BATCH_SIZE}")
    print(f"  Learning rate: {config.LEARNING_RATE}")
    print(f"  Epochs: {config.NUM_EPOCHS}")
    print(f"  FP16: {training_args.fp16}")
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
    
    # Train
    print(f"\n🏋️ Training started...")
    train_result = trainer.train()
    
    # Save model
    trainer.save_model(output_dir)
    print(f"\n✓ Model saved to {output_dir}")
    
    # Evaluate on test set
    print(f"\n📊 Evaluating on test set...")
    test_results = trainer.evaluate(test_dataset)
    
    print(f"\n✅ TRAINING COMPLETE!")
    print(f"\n📈 Test Set Results:")
    for key, value in test_results.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
    
    return trainer, test_results


# ==================== INFERENCE ====================

def predict_emphasis(text, model_path='./outputs/checkpoints'):
    """Predict emphasis in a given sentence"""
    import config
    
    # Load model and tokenizer
    tokenizer = BertTokenizerFast.from_pretrained(model_path)
    model = BertForTokenClassification.from_pretrained(model_path)
    model.eval()
    
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
    
    # Predict
    with torch.no_grad():
        outputs = model(**encoding)
        predictions = torch.argmax(outputs.logits, dim=2)
    
    # Align predictions with words
    word_ids = encoding.word_ids()
    predicted_labels = []
    
    prev_word_idx = None
    for word_idx, pred in zip(word_ids, predictions[0].tolist()):
        if word_idx is not None and word_idx != prev_word_idx:
            predicted_labels.append(config.ID2LABEL[pred])
            prev_word_idx = word_idx
    
    # Create highlighted output
    result = []
    for word, label in zip(words, predicted_labels):
        if label.startswith('B-') or label.startswith('I-'):
            result.append(f"**{word}**")
        else:
            result.append(word)
    
    return {
        'original': text,
        'words': words,
        'labels': predicted_labels,
        'highlighted': ' '.join(result)
    }


# ==================== MAIN ====================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--predict':
        # Inference mode
        if len(sys.argv) < 3:
            print("Usage: python token-classification.py --predict 'Your Turkish sentence here'")
            sys.exit(1)
        
        sentence = sys.argv[2]
        result = predict_emphasis(sentence)
        
        print(f"\n📝 Prediction:")
        print(f"Original: {result['original']}")
        print(f"Words: {result['words']}")
        print(f"Labels: {result['labels']}")
        print(f"Highlighted: {result['highlighted']}")
    else:
        # Training mode
        trainer, results = train_model()
        
        # Save results
        import json
        import config
        results_path = config.RESULTS_DIR / 'test_results.json'
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to {results_path}")