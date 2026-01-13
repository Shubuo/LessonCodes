"""
Weighted Loss Module
Implements class-weighted CrossEntropyLoss for handling class imbalance
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Optional
import numpy as np


def compute_class_weights(class_counts: List[int], method: str = "inverse") -> torch.Tensor:
    """
    Compute class weights based on frequency
    
    Formula: w_c = N_total / (K × N_c)
    
    Args:
        class_counts: [count_O, count_B, count_I]
        method: "inverse" (1/freq), "sqrt_inverse", or "effective"
    
    Returns:
        Tensor of class weights
    """
    total = sum(class_counts)
    num_classes = len(class_counts)
    
    if method == "inverse":
        # Standard inverse frequency
        # w_c = N_total / (K × N_c)
        weights = [total / (num_classes * count) if count > 0 else 0 
                   for count in class_counts]
    
    elif method == "sqrt_inverse":
        # Square root of inverse (less aggressive)
        weights = [np.sqrt(total / (num_classes * count)) if count > 0 else 0 
                   for count in class_counts]
    
    elif method == "effective":
        # Effective number of samples (CB Loss)
        # w_c = (1 - β^n) / (1 - β) where β = (N-1)/N
        beta = 0.9999
        weights = []
        for count in class_counts:
            if count > 0:
                effective = (1 - beta**count) / (1 - beta)
                weights.append(1 / effective)
            else:
                weights.append(0)
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Normalize so minimum weight is 1.0
    min_weight = min(w for w in weights if w > 0)
    weights = [w / min_weight for w in weights]
    
    return torch.tensor(weights, dtype=torch.float32)


class WeightedCrossEntropyLoss(nn.Module):
    """
    Cross-entropy loss with class weights for token classification
    """
    
    def __init__(self, class_counts: List[int], ignore_index: int = -100, 
                 method: str = "inverse"):
        super().__init__()
        
        self.weights = compute_class_weights(class_counts, method)
        self.ignore_index = ignore_index
        
        print(f"Class weights ({method}): {self.weights.tolist()}")
    
    def forward(self, logits: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logits: (batch_size, seq_len, num_classes)
            labels: (batch_size, seq_len)
        
        Returns:
            Weighted loss scalar
        """
        # Move weights to same device
        weights = self.weights.to(logits.device)
        
        # Flatten for loss computation
        logits_flat = logits.view(-1, logits.size(-1))
        labels_flat = labels.view(-1)
        
        # Compute weighted cross-entropy
        loss = F.cross_entropy(
            logits_flat, 
            labels_flat,
            weight=weights,
            ignore_index=self.ignore_index,
            reduction='mean'
        )
        
        return loss


class FocalLoss(nn.Module):
    """
    Focal Loss for handling class imbalance
    FL(p) = -α(1-p)^γ log(p)
    
    Focuses training on hard examples (low confidence predictions)
    """
    
    def __init__(self, gamma: float = 2.0, alpha: Optional[List[float]] = None,
                 ignore_index: int = -100):
        super().__init__()
        
        self.gamma = gamma
        self.alpha = torch.tensor(alpha) if alpha else None
        self.ignore_index = ignore_index
        
        print(f"Focal Loss: gamma={gamma}, alpha={alpha}")
    
    def forward(self, logits: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logits: (batch_size, seq_len, num_classes)
            labels: (batch_size, seq_len)
        """
        # Flatten
        batch_size, seq_len, num_classes = logits.shape
        logits_flat = logits.view(-1, num_classes)
        labels_flat = labels.view(-1)
        
        # Create mask for valid tokens
        valid_mask = labels_flat != self.ignore_index
        
        # Get predictions only for valid tokens
        logits_valid = logits_flat[valid_mask]
        labels_valid = labels_flat[valid_mask]
        
        if logits_valid.size(0) == 0:
            return torch.tensor(0.0, device=logits.device)
        
        # Compute softmax probabilities
        probs = F.softmax(logits_valid, dim=-1)
        
        # Get probability of correct class
        ce_loss = F.cross_entropy(logits_valid, labels_valid, reduction='none')
        pt = torch.exp(-ce_loss)  # pt = p_correct
        
        # Focal weight
        focal_weight = (1 - pt) ** self.gamma
        
        # Alpha weighting
        if self.alpha is not None:
            alpha = self.alpha.to(logits.device)
            alpha_t = alpha[labels_valid]
            focal_weight = alpha_t * focal_weight
        
        # Final loss
        loss = (focal_weight * ce_loss).mean()
        
        return loss


# Pre-computed weights based on project data
# O: 3023, B-EMPHASIS: 765, I-EMPHASIS: 27
DEFAULT_CLASS_COUNTS = [3023, 765, 27]


def get_default_weights():
    """Get default weights for Turkish emphasis detection"""
    return compute_class_weights(DEFAULT_CLASS_COUNTS, method="inverse")


if __name__ == "__main__":
    print("Testing Weighted Loss Module\n")
    print("="*50)
    
    # Test weight computation
    counts = [3023, 765, 27]  # O, B-EMPHASIS, I-EMPHASIS
    
    print("\n1. Inverse frequency weights:")
    w1 = compute_class_weights(counts, "inverse")
    print(f"   O: {w1[0]:.2f}, B: {w1[1]:.2f}, I: {w1[2]:.2f}")
    
    print("\n2. Sqrt inverse weights:")
    w2 = compute_class_weights(counts, "sqrt_inverse")
    print(f"   O: {w2[0]:.2f}, B: {w2[1]:.2f}, I: {w2[2]:.2f}")
    
    print("\n3. Effective number weights:")
    w3 = compute_class_weights(counts, "effective")
    print(f"   O: {w3[0]:.2f}, B: {w3[1]:.2f}, I: {w3[2]:.2f}")
    
    # Test loss computation
    print("\n" + "="*50)
    print("Testing loss computation:")
    
    # Mock data
    batch_size, seq_len, num_classes = 2, 5, 3
    logits = torch.randn(batch_size, seq_len, num_classes)
    labels = torch.tensor([[0, 1, 0, 0, -100], [0, 0, 1, 2, 0]])
    
    # Weighted CE
    weighted_loss = WeightedCrossEntropyLoss(counts)
    loss1 = weighted_loss(logits, labels)
    print(f"Weighted CE Loss: {loss1.item():.4f}")
    
    # Focal Loss
    focal_loss = FocalLoss(gamma=2.0, alpha=[1.0, 4.0, 47.0])
    loss2 = focal_loss(logits, labels)
    print(f"Focal Loss: {loss2.item():.4f}")
