"""
Evaluation module for Turkish Stress Detection
Implements discourse-aware evaluation and contrastive test sets
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import confusion_matrix, classification_report, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
import config


def load_predictions(model_path, test_data_path):
    """Load test data and generate predictions"""
    from transformers import BertTokenizerFast, BertForTokenClassification
    import torch
    
    # Load model
    tokenizer = BertTokenizerFast.from_pretrained(model_path)
    model = BertForTokenClassification.from_pretrained(model_path)
    model.eval()
    
    # Load test data
    with open(test_data_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    all_true_labels = []
    all_pred_labels = []
    predictions_detailed = []
    
    for example in test_data:
        words = example['words']
        true_labels = example['label_ids']
        
        # Tokenize
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
        
        # Align predictions
        word_ids = encoding.word_ids()
        pred_labels = []
        
        prev_word_idx = None
        for word_idx, pred in zip(word_ids, predictions[0].tolist()):
            if word_idx is not None and word_idx != prev_word_idx:
                pred_labels.append(pred)
                prev_word_idx = word_idx
        
        # Store
        all_true_labels.extend(true_labels)
        all_pred_labels.extend(pred_labels)
        
        predictions_detailed.append({
            'id': example['id'],
            'words': words,
            'true_labels': [config.ID2LABEL[l] for l in true_labels],
            'pred_labels': [config.ID2LABEL[l] for l in pred_labels],
            'true_ids': true_labels,
            'pred_ids': pred_labels
        })
    
    return all_true_labels, all_pred_labels, predictions_detailed


def compute_confusion_matrix(true_labels, pred_labels, save_path=None):
    """Compute and visualize confusion matrix"""
    cm = confusion_matrix(true_labels, pred_labels)
    
    # Create figure
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=list(config.LABEL2ID.keys()),
        yticklabels=list(config.LABEL2ID.keys()),
        cbar_kws={'label': 'Count'}
    )
    plt.xlabel('Predicted Label', fontsize=12)
    plt.ylabel('True Label', fontsize=12)
    plt.title('Confusion Matrix - Turkish Stress Detection', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Confusion matrix saved to {save_path}")
    
    return cm


def compute_metrics_per_class(true_labels, pred_labels):
    """Compute precision, recall, F1 per class"""
    report = classification_report(
        true_labels,
        pred_labels,
        target_names=list(config.LABEL2ID.keys()),
        output_dict=True,
        zero_division=0
    )
    
    # Convert to DataFrame for easier viewing
    df = pd.DataFrame(report).transpose()
    
    return df


def evaluate_contrastive_tests():
    """Evaluate on contrastive test pairs"""
    # Define contrastive pairs
    # Each pair tests if the model understands different emphasis placements
    contrastive_pairs = [
        {
            'context': 'Okula giden kimdi?',
            'options': [
                {'text': 'Ali okula gitti', 'correct_emphasis': 'Ali'},
                {'text': 'Okula Ali gitti', 'correct_emphasis': 'Ali'}
            ]
        },
        {
            'context': 'Ne zaman gelecek?',
            'options': [
                {'text': 'Yarın Ali gelecek', 'correct_emphasis': 'Yarın'},
                {'text': 'Ali yarın gelecek', 'correct_emphasis': 'yarın'}
            ]
        },
        {
            'context': 'Nereye gitti?',
            'options': [
                {'text': 'Okula Ali gitti', 'correct_emphasis': 'Okula'},
                {'text': 'Ali okula gitti', 'correct_emphasis': 'okula'}
            ]
        }
    ]
    
    print("\n" + "="*60)
    print("CONTRASTIVE TEST EVALUATION")
    print("="*60)
    print("\nNote: This demonstrates the concept. For full evaluation,")
    print("load a trained model and predict emphasis for each option.")
    print("\nContrastive pairs examples:")
    
    for i, pair in enumerate(contrastive_pairs, 1):
        print(f"\n{i}. Context: {pair['context']}")
        for j, option in enumerate(pair['options'], 1):
            print(f"   Option {j}: {option['text']}")
            print(f"   Expected emphasis: {option['correct_emphasis']}")
    
    return contrastive_pairs


def create_evaluation_report(true_labels, pred_labels, predictions_detailed, output_dir):
    """Create comprehensive evaluation report"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("📊 GENERATING EVALUATION REPORT")
    print("="*60)
    
    # 1. Overall metrics
    print("\n1️⃣ Computing overall metrics...")
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    accuracy = accuracy_score(true_labels, pred_labels)
    precision = precision_score(true_labels, pred_labels, average='weighted', zero_division=0)
    recall = recall_score(true_labels, pred_labels, average='weighted', zero_division=0)
    f1 = f1_score(true_labels, pred_labels, average='weighted', zero_division=0)
    
    metrics = {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1': float(f1)
    }
    
    print(f"   Accuracy: {accuracy:.4f}")
    print(f"   Precision: {precision:.4f}")
    print(f"   Recall: {recall:.4f}")
    print(f"   F1 Score: {f1:.4f}")
    
    # 2. Per-class metrics
    print("\n2️⃣ Computing per-class metrics...")
    per_class_df = compute_metrics_per_class(true_labels, pred_labels)
    per_class_path = output_dir / 'per_class_metrics.csv'
    per_class_df.to_csv(per_class_path)
    print(f"   ✓ Saved to {per_class_path}")
    
    # 3. Confusion matrix
    print("\n3️⃣ Generating confusion matrix...")
    cm_path = output_dir / 'confusion_matrix.png'
    cm = compute_confusion_matrix(true_labels, pred_labels, save_path=cm_path)
    
    # 4. Sample predictions
    print("\n4️⃣ Selecting sample predictions...")
    sample_predictions = predictions_detailed[:20]
    sample_path = output_dir / 'sample_predictions.json'
    with open(sample_path, 'w', encoding='utf-8') as f:
        json.dump(sample_predictions, f, ensure_ascii=False, indent=2)
    print(f"   ✓ Saved to {sample_path}")
    
    # 5. Save all metrics
    metrics_path = output_dir / 'evaluation_metrics.json'
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\n✓ Overall metrics saved to {metrics_path}")
    
    # 6. Contrastive tests
    print("\n5️⃣ Demonstrating contrastive tests...")
    contrastive_pairs = evaluate_contrastive_tests()
    
    print("\n" + "="*60)
    print("✅ EVALUATION REPORT COMPLETE")
    print("="*60)
    print(f"\nResults saved to: {output_dir}")
    
    return metrics, per_class_df, cm


def main():
    """Main evaluation function"""
    import sys
    
    model_path = config.CHECKPOINTS_DIR
    test_data_path = config.PROCESSED_DIR / 'test.json'
    output_dir = config.RESULTS_DIR
    
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        print("   Please train the model first: python token-classification.py")
        return
    
    if not test_data_path.exists():
        print(f"❌ Test data not found: {test_data_path}")
        print("   Please run data_loader.py first")
        return
    
    print("\n" + "="*60)
    print("🔍 TURKISH STRESS DETECTION - EVALUATION")
    print("="*60)
    
    # Load predictions
    print("\n📥 Loading model and generating predictions...")
    true_labels, pred_labels, predictions_detailed = load_predictions(
        str(model_path), str(test_data_path)
    )
    print(f"  ✓ Generated predictions for {len(predictions_detailed)} examples")
    
    # Create evaluation report
    metrics, per_class_df, cm = create_evaluation_report(
        true_labels, pred_labels, predictions_detailed, output_dir
    )
    
    print("\n📈 Summary:")
    print(f"  F1 Score: {metrics['f1']:.4f}")
    print(f"  Accuracy: {metrics['accuracy']:.4f}")


if __name__ == "__main__":
    main()
