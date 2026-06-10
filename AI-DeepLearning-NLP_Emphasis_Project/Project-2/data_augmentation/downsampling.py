"""
Downsampling Strategy (Strategy D)
Reduces O-class dominance to balance the dataset
"""
import random
from typing import List, Tuple
from collections import Counter
import json


def calculate_class_distribution(samples: List[dict]) -> dict:
    """Calculate current class distribution"""
    counts = Counter()
    
    for sample in samples:
        for tag in sample.get('bio_tags', []):
            counts[tag] += 1
    
    total = sum(counts.values())
    distribution = {tag: count/total*100 for tag, count in counts.items()}
    
    return {"counts": dict(counts), "percentages": distribution}


def downsample_o_class(samples: List[dict], target_o_ratio: float = 0.50) -> List[dict]:
    """
    Downsample sentences with mostly O tags to reduce class imbalance
    
    Args:
        samples: List of samples in dict format
        target_o_ratio: Target percentage of O tags (default 50%)
    
    Returns:
        Balanced list of samples
    """
    # Separate samples by emphasis ratio
    emphasis_samples = []  # Has B-EMPHASIS or I-EMPHASIS
    neutral_samples = []   # Only O tags
    
    for sample in samples:
        tags = sample.get('bio_tags', [])
        has_emphasis = any(tag in ['B-EMPHASIS', 'I-EMPHASIS'] for tag in tags)
        
        if has_emphasis:
            emphasis_samples.append(sample)
        else:
            neutral_samples.append(sample)
    
    # Calculate current O ratio
    current_dist = calculate_class_distribution(samples)
    current_o_ratio = current_dist['percentages'].get('O', 0) / 100
    
    print(f"Current O ratio: {current_o_ratio:.2%}")
    print(f"Target O ratio: {target_o_ratio:.2%}")
    print(f"Emphasis samples: {len(emphasis_samples)}")
    print(f"Neutral samples: {len(neutral_samples)}")
    
    # Calculate how many neutral samples to keep
    # We want: O_total / (O_total + B + I) = target_o_ratio
    # This means keeping emphasis samples and limiting neutral ones
    
    # First, keep all emphasis samples
    balanced_samples = emphasis_samples.copy()
    
    # Calculate O tokens in emphasis samples
    o_in_emphasis = sum(
        sum(1 for tag in s['bio_tags'] if tag == 'O')
        for s in emphasis_samples
    )
    
    # Calculate target neutral samples to keep
    # We limit neutral samples to achieve balance
    total_emphasis_tokens = sum(
        sum(1 for tag in s['bio_tags'] if tag in ['B-EMPHASIS', 'I-EMPHASIS'])
        for s in emphasis_samples
    )
    
    # Target: O tokens should be target_o_ratio of total
    # O = o_in_emphasis + o_from_neutral
    # total = O + B + I = O + total_emphasis_tokens
    # O / total = target_o_ratio
    # O = target_o_ratio * (O + total_emphasis_tokens)
    # O * (1 - target_o_ratio) = target_o_ratio * total_emphasis_tokens
    # O = target_o_ratio * total_emphasis_tokens / (1 - target_o_ratio)
    
    target_o = target_o_ratio * total_emphasis_tokens / (1 - target_o_ratio)
    additional_o_needed = max(0, target_o - o_in_emphasis)
    
    # Calculate average O tokens per neutral sample
    if neutral_samples:
        avg_o_per_neutral = sum(len(s['bio_tags']) for s in neutral_samples) / len(neutral_samples)
        neutral_to_keep = int(additional_o_needed / avg_o_per_neutral)
        neutral_to_keep = min(neutral_to_keep, len(neutral_samples))
        
        # Randomly select neutral samples
        random.shuffle(neutral_samples)
        balanced_samples.extend(neutral_samples[:neutral_to_keep])
        
        print(f"Keeping {neutral_to_keep} neutral samples (from {len(neutral_samples)})")
    
    # Shuffle final dataset
    random.shuffle(balanced_samples)
    
    # Verify new distribution
    new_dist = calculate_class_distribution(balanced_samples)
    print(f"New O ratio: {new_dist['percentages'].get('O', 0):.1f}%")
    print(f"Final dataset size: {len(balanced_samples)} samples")
    
    return balanced_samples


def oversample_minority_class(samples: List[dict], target_b_ratio: float = 0.35) -> List[dict]:
    """
    Oversample B-EMPHASIS and I-EMPHASIS samples to increase their representation
    
    Args:
        samples: List of samples
        target_b_ratio: Target B-EMPHASIS ratio
    
    Returns:
        Oversampled list
    """
    current_dist = calculate_class_distribution(samples)
    b_count = current_dist['counts'].get('B-EMPHASIS', 0)
    total = sum(current_dist['counts'].values())
    
    # Calculate how many times to duplicate emphasis samples
    target_b = target_b_ratio * total / (1 - target_b_ratio)
    multiplier = max(1, int(target_b / b_count)) if b_count > 0 else 1
    
    print(f"Oversampling multiplier: {multiplier}x")
    
    oversampled = []
    for sample in samples:
        tags = sample.get('bio_tags', [])
        has_emphasis = any(tag in ['B-EMPHASIS', 'I-EMPHASIS'] for tag in tags)
        
        if has_emphasis:
            # Duplicate emphasis samples
            for _ in range(multiplier):
                oversampled.append(sample.copy())
        else:
            oversampled.append(sample)
    
    random.shuffle(oversampled)
    
    new_dist = calculate_class_distribution(oversampled)
    print(f"After oversampling:")
    print(f"  O: {new_dist['percentages'].get('O', 0):.1f}%")
    print(f"  B-EMPHASIS: {new_dist['percentages'].get('B-EMPHASIS', 0):.1f}%")
    print(f"  I-EMPHASIS: {new_dist['percentages'].get('I-EMPHASIS', 0):.1f}%")
    
    return oversampled


def balance_dataset(samples: List[dict], 
                   target_o: float = 0.50, 
                   target_b: float = 0.40,
                   target_i: float = 0.10) -> List[dict]:
    """
    Balance dataset using both downsampling and oversampling
    
    Target distribution:
    - O: 50%
    - B-EMPHASIS: 40%
    - I-EMPHASIS: 10%
    """
    print("\n" + "="*50)
    print("DATASET BALANCING")
    print("="*50)
    
    print("\n[Step 1] Initial distribution:")
    initial_dist = calculate_class_distribution(samples)
    for tag, pct in initial_dist['percentages'].items():
        print(f"  {tag}: {pct:.1f}%")
    
    print(f"\n[Step 2] Downsampling O class...")
    balanced = downsample_o_class(samples, target_o_ratio=target_o)
    
    print(f"\n[Step 3] Oversampling emphasis classes...")
    balanced = oversample_minority_class(balanced, target_b_ratio=target_b)
    
    print(f"\n[Step 4] Final distribution:")
    final_dist = calculate_class_distribution(balanced)
    for tag, pct in final_dist['percentages'].items():
        print(f"  {tag}: {pct:.1f}%")
    
    print(f"\nDataset size: {len(samples)} → {len(balanced)}")
    
    return balanced


if __name__ == "__main__":
    # Test with mock data
    mock_samples = [
        {"bio_tags": ["O", "O", "O", "O"]},  # Neutral
        {"bio_tags": ["B-EMPHASIS", "O", "O", "O"]},  # Subject emphasis
        {"bio_tags": ["O", "B-EMPHASIS", "O", "O"]},  # Object emphasis
        {"bio_tags": ["O", "O", "O", "O"]},  # Neutral
        {"bio_tags": ["O", "O", "O", "O"]},  # Neutral
        {"bio_tags": ["B-EMPHASIS", "I-EMPHASIS", "O", "O"]},  # Multi-word
    ]
    
    # Replicate to simulate larger dataset
    mock_samples = mock_samples * 100
    
    balanced = balance_dataset(mock_samples)
