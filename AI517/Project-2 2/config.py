"""
Configuration file for Turkish Stress Detection Project
Centralized settings for paths, model hyperparameters, and training parameters
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
LEGACY_DIR = PROJECT_ROOT / "legacy"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Legacy dataset paths
VURGU_VARYASYONLARI_PATH = LEGACY_DIR / "vurgu_varyasyonlari.csv"
VURGU_HECE_PATH = LEGACY_DIR / "vurguHece.csv"

# Output paths
FIGURES_DIR = OUTPUT_DIR / "figures"
CHECKPOINTS_DIR = OUTPUT_DIR / "checkpoints"
LOGS_DIR = OUTPUT_DIR / "logs"
RESULTS_DIR = OUTPUT_DIR / "results"

# Create directories if they don't exist
for directory in [DATA_DIR, PROCESSED_DIR, OUTPUT_DIR, FIGURES_DIR, 
                  CHECKPOINTS_DIR, LOGS_DIR, RESULTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Model configuration
MODEL_CHECKPOINT = "dbmdz/bert-base-turkish-cased"  # Turkish BERT model
MAX_LENGTH = 128  # Maximum sequence length
NUM_LABELS = 3  # O, B-EMPHASIS, I-EMPHASIS (BIO tagging)

# Training hyperparameters
BATCH_SIZE = 8  # Reduced for CPU
LEARNING_RATE = 2e-5
NUM_EPOCHS = 3  # Reduced for faster training on CPU
WARMUP_STEPS = 200  # Reduced proportionally
WEIGHT_DECAY = 0.01
GRADIENT_ACCUMULATION_STEPS = 2  # Simulate larger batch size
FP16 = False  # Disabled for CPU (FP16 requires GPU)

# Data split ratios
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Random seed for reproducibility
RANDOM_SEED = 42

# Label mappings
LABEL2ID = {
    "O": 0,           # Outside (no emphasis)
    "B-EMPHASIS": 1,  # Begin emphasis
    "I-EMPHASIS": 2   # Inside emphasis
}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}

# Focus type mappings (for analysis)
FOCUS_TYPES = {
    "subject": "Özne",
    "object": "Nesne",
    "time": "Zaman",
    "location": "Yer",
    "manner": "Tarz",
    "verb": "Fiil",
    "predicate": "Yüklem"
}

# Evaluation settings
EVALUATION_STRATEGY = "epoch"
SAVE_STRATEGY = "epoch"
LOAD_BEST_MODEL_AT_END = True
METRIC_FOR_BEST_MODEL = "f1"
GREATER_IS_BETTER = True

# Logging
LOGGING_STEPS = 50
LOGGING_DIR = str(LOGS_DIR)

print(f"✓ Configuration loaded")
print(f"  - Legacy data: {LEGACY_DIR}")
print(f"  - Processed data: {PROCESSED_DIR}")
print(f"  - Outputs: {OUTPUT_DIR}")
print(f"  - Model: {MODEL_CHECKPOINT}")
