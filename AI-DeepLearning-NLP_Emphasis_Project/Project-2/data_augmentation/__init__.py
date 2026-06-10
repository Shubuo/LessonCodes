"""
Data Augmentation Package
Combines all augmentation strategies for Turkish Emphasis Detection v2.0
"""
from .schema import EmphasisSample, create_bio_tags, validate_sample, save_jsonl, load_jsonl, FOCUS_TYPES
from .focus_shifting import FocusShifter, BASE_SENTENCES
from .morphological import MorphologicalAugmenter
from .downsampling import balance_dataset, calculate_class_distribution, downsample_o_class, oversample_minority_class

__all__ = [
    # Schema
    'EmphasisSample',
    'create_bio_tags',
    'validate_sample',
    'save_jsonl',
    'load_jsonl',
    'FOCUS_TYPES',
    
    # Augmentation
    'FocusShifter',
    'MorphologicalAugmenter',
    'BASE_SENTENCES',
    
    # Balancing
    'balance_dataset',
    'calculate_class_distribution',
    'downsample_o_class',
    'oversample_minority_class',
]
