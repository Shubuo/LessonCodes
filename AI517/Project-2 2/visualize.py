"""
Visualization module for Turkish Stress Detection
Creates publication-ready figures and tables
"""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import config


# Set publication-quality defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'
sns.set_style("whitegrid")


def plot_training_curves(log_history, save_dir):
    """Plot training and validation loss/metrics over epochs"""
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract metrics from log history
    train_loss = [entry['loss'] for entry in log_history if 'loss' in entry]
    eval_loss = [entry['eval_loss'] for entry in log_history if 'eval_loss' in entry]
    eval_f1 = [entry.get('eval_f1', None) for entry in log_history if 'eval_f1' in entry]
    
    epochs_train = np.arange(1, len(train_loss) + 1)
    epochs_eval = np.linspace(1, len(train_loss), len(eval_loss))
    
    # Create figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Loss curves
    axes[0].plot(epochs_train, train_loss, 'b-', label='Training Loss', linewidth=2)
    if eval_loss:
        axes[0].plot(epochs_eval, eval_loss, 'r-', label='Validation Loss', linewidth=2)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss', fontsize=12)
    axes[0].set_title('Training and Validation Loss', fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: F1 score
    if eval_f1 and any(f is not None for f in eval_f1):
        axes[1].plot(epochs_eval, eval_f1, 'g-', linewidth=2, marker='o')
        axes[1].set_xlabel('Epoch', fontsize=12)
        axes[1].set_ylabel('F1 Score', fontsize=12)
        axes[1].set_title('Validation F1 Score', fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        axes[1].set_ylim([0, 1])
    else:
        axes[1].text(0.5, 0.5, 'F1 scores not available', 
                    ha='center', va='center', transform=axes[1].transAxes)
        axes[1].set_title('Validation F1 Score', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    save_path = save_dir / 'training_curves.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Training curves saved to {save_path}")
    
    plt.close()


def create_performance_table(metrics_dict, save_dir):
    """Create a table of performance metrics"""
    save_dir = Path(save_dir)
    
    # Create DataFrame
    df = pd.DataFrame([metrics_dict])
    df = df[['accuracy', 'precision', 'recall', 'f1']]
    df.columns = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
    
    # Format as percentages
    df = (df * 100).round(2)
    
    # Save as CSV
    csv_path = save_dir / 'performance_summary.csv'
    df.to_csv(csv_path, index=False)
    print(f"✓ Performance table saved to {csv_path}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        colWidths=[0.2] * len(df.columns)
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)
    
    # Style header
    for i in range(len(df.columns)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style cells
    for i in range(1, len(df) + 1):
        for j in range(len(df.columns)):
            table[(i, j)].set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
    
    plt.title('Model Performance Summary', fontsize=14, fontweight='bold', pad=20)
    
    table_path = save_dir / 'performance_table.png'
    plt.savefig(table_path, dpi=300, bbox_inches='tight')
    print(f"✓ Performance table figure saved to {table_path}")
    
    plt.close()
    
    return df


def visualize_sample_predictions(predictions, save_dir, n_samples=10):
    """Create HTML visualization of sample predictions"""
    save_dir = Path(save_dir)
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            .prediction {
                background: white;
                margin: 20px 0;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .sentence {
                font-size: 18px;
                margin: 10px 0;
                line-height: 1.6;
            }
            .word {
                display: inline-block;
                margin: 2px 4px;
                padding: 4px 8px;
                border-radius: 4px;
            }
            .emphasis {
                background: #ffeb3b;
                font-weight: bold;
                border: 2px solid #ffc107;
            }
            .correct {
                background: #4caf50;
                color: white;
            }
            .incorrect {
                background: #f44336;
                color: white;
            }
            .labels {
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }
            .score {
                font-size: 14px;
                color: #555;
            }
        </style>
    </head>
    <body>
        <h1>🔍 Turkish Stress Detection - Sample Predictions</h1>
    """
    
    for i, pred in enumerate(predictions[:n_samples], 1):
        words = pred['words']
        true_labels = pred['true_labels']
        pred_labels = pred['pred_labels']
        
        # Calculate accuracy for this example
        correct = sum(1 for t, p in zip(true_labels, pred_labels) if t == p)
        accuracy = correct / len(true_labels) * 100
        
        html_content += f"""
        <div class="prediction">
            <h3>Example {i}</h3>
            <div class="score">Word-level Accuracy: {accuracy:.1f}%</div>
            
            <div class="sentence">
                <strong>Original:</strong><br>
        """
        
        for word, true_label, pred_label in zip(words, true_labels, pred_labels):
            is_emphasis = true_label.startswith('B-') or true_label.startswith('I-')
            is_correct = true_label == pred_label
            
            css_class = "word"
            if is_emphasis:
                css_class += " emphasis"
            if not is_correct:
                css_class += " incorrect"
            
            html_content += f'<span class="{css_class}" title="True: {true_label}, Pred: {pred_label}">{word}</span>'
        
        html_content += """
            </div>
            <div class="labels">
                <strong>True labels:</strong> """ + ", ".join(true_labels) + """<br>
                <strong>Pred labels:</strong> """ + ", ".join(pred_labels) + """
            </div>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    html_path = save_dir / 'sample_predictions.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Sample predictions HTML saved to {html_path}")


def create_label_distribution_plot(predictions, save_dir):
    """Plot distribution of predicted vs true labels"""
    save_dir = Path(save_dir)
    
    # Count labels
    true_counts = {}
    pred_counts = {}
    
    for pred in predictions:
        for true_label in pred['true_labels']:
            true_counts[true_label] = true_counts.get(true_label, 0) + 1
        for pred_label in pred['pred_labels']:
            pred_counts[pred_label] = pred_counts.get(pred_label, 0) + 1
    
    # Create DataFrame
    labels = sorted(set(list(true_counts.keys()) + list(pred_counts.keys())))
    data = {
        'Label': labels,
        'True': [true_counts.get(l, 0) for l in labels],
        'Predicted': [pred_counts.get(l, 0) for l in labels]
    }
    df = pd.DataFrame(data)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(labels))
    width = 0.35
    
    ax.bar(x - width/2, df['True'], width, label='True Labels', color='#2196F3', alpha=0.8)
    ax.bar(x + width/2, df['Predicted'], width, label='Predicted Labels', color='#FF9800', alpha=0.8)
    
    ax.set_xlabel('Label', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Label Distribution: True vs Predicted', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    save_path = save_dir / 'label_distribution.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Label distribution plot saved to {save_path}")
    
    plt.close()


def main():
    """Main visualization function"""
    results_dir = config.RESULTS_DIR
    figures_dir = config.FIGURES_DIR
    
    print("\n" + "="*60)
    print("📊 GENERATING VISUALIZATIONS")
    print("="*60)
    
    # Load evaluation metrics
    metrics_path = results_dir / 'evaluation_metrics.json'
    if metrics_path.exists():
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        print("\n1️⃣ Creating performance table...")
        create_performance_table(metrics, figures_dir)
    
    # Load sample predictions
    predictions_path = results_dir / 'sample_predictions.json'
    if predictions_path.exists():
        with open(predictions_path, 'r', encoding='utf-8') as f:
            predictions = json.load(f)
        
        print("\n2️⃣ Creating sample predictions HTML...")
        visualize_sample_predictions(predictions, figures_dir, n_samples=15)
        
        print("\n3️⃣ Creating label distribution plot...")
        create_label_distribution_plot(predictions, figures_dir)
    
    # Note: Training curves require trainer.state.log_history
    # This will be generated during training
    
    print("\n" + "="*60)
    print("✅ VISUALIZATION COMPLETE")
    print("="*60)
    print(f"\nAll figures saved to: {figures_dir}")
    print("\nGenerated files:")
    print("  - performance_summary.csv")
    print("  - performance_table.png")
    print("  - sample_predictions.html")
    print("  - label_distribution.png")
    print("  - confusion_matrix.png (from evaluation.py)")


if __name__ == "__main__":
    main()
