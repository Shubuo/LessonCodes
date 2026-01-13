"""
JSONL Schema for Turkish Stress Detection v2.0
Defines the enriched data format with contrastive pairs and context questions
"""
from dataclasses import dataclass, asdict
from typing import List, Optional
import json

@dataclass
class EmphasisSample:
    """Single sample in the emphasis dataset"""
    id: str
    sentence: str
    focus_token: str
    focus_type: str  # SUBJECT_FOCUS, OBJECT_FOCUS, TIME_FOCUS, LOCATION_FOCUS, VERB_FOCUS
    tokens: List[str]
    bio_tags: List[str]  # B-EMPHASIS, I-EMPHASIS, O
    contrastive_pair: Optional[str] = None
    context_question: Optional[str] = None
    source: str = "generated"
    
    def to_dict(self):
        return asdict(self)
    
    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str):
        return cls.from_dict(json.loads(json_str))


# Focus type definitions
FOCUS_TYPES = {
    "SUBJECT_FOCUS": {
        "tr": "Özne Vurgusu",
        "questions": ["Kim?", "Ne?", "Kimler?"],
        "description": "Cümlede öznenin vurgulanması"
    },
    "OBJECT_FOCUS": {
        "tr": "Nesne Vurgusu",
        "questions": ["Neyi?", "Kimi?", "Ne?"],
        "description": "Cümlede nesnenin vurgulanması"
    },
    "TIME_FOCUS": {
        "tr": "Zaman Vurgusu",
        "questions": ["Ne zaman?", "Hangi gün?", "Saat kaçta?"],
        "description": "Zaman zarfının vurgulanması"
    },
    "LOCATION_FOCUS": {
        "tr": "Yer Vurgusu",
        "questions": ["Nerede?", "Nereye?", "Nereden?"],
        "description": "Yer zarfının vurgulanması"
    },
    "VERB_FOCUS": {
        "tr": "Fiil Vurgusu",
        "questions": ["Ne yaptı?", "Ne oldu?"],
        "description": "Yüklemin vurgulanması"
    },
    "MANNER_FOCUS": {
        "tr": "Tarz Vurgusu",
        "questions": ["Nasıl?", "Ne şekilde?"],
        "description": "Tarz zarfının vurgulanması"
    }
}


def create_bio_tags(tokens: List[str], focus_token: str) -> List[str]:
    """
    Create BIO tags for a token list based on focus token
    Handles multi-word focus tokens (I-EMPHASIS)
    """
    bio_tags = []
    focus_words = focus_token.split()
    in_focus = False
    focus_idx = 0
    
    for token in tokens:
        # Check if this token matches the current focus word
        if focus_idx < len(focus_words) and token.lower() == focus_words[focus_idx].lower():
            if focus_idx == 0:
                bio_tags.append("B-EMPHASIS")
            else:
                bio_tags.append("I-EMPHASIS")
            focus_idx += 1
            in_focus = True
        else:
            bio_tags.append("O")
            if in_focus:
                # Reset if we're past the focus
                focus_idx = 0
                in_focus = False
    
    return bio_tags


def validate_sample(sample: EmphasisSample) -> bool:
    """Validate a sample for correctness"""
    # Check lengths match
    if len(sample.tokens) != len(sample.bio_tags):
        return False
    
    # Check BIO validity (I can only follow B or I)
    prev_tag = "O"
    for tag in sample.bio_tags:
        if tag == "I-EMPHASIS" and prev_tag == "O":
            return False
        prev_tag = tag
    
    # Check focus token exists in sentence
    if sample.focus_token.lower() not in sample.sentence.lower():
        return False
    
    return True


def save_jsonl(samples: List[EmphasisSample], filepath: str):
    """Save samples to JSONL file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        for sample in samples:
            f.write(sample.to_json() + '\n')
    print(f"✓ Saved {len(samples)} samples to {filepath}")


def load_jsonl(filepath: str) -> List[EmphasisSample]:
    """Load samples from JSONL file"""
    samples = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                samples.append(EmphasisSample.from_json(line))
    print(f"✓ Loaded {len(samples)} samples from {filepath}")
    return samples


# Example usage
if __name__ == "__main__":
    # Create a sample
    sample = EmphasisSample(
        id="sample_001",
        sentence="Ali eve geldi.",
        focus_token="Ali",
        focus_type="SUBJECT_FOCUS",
        tokens=["Ali", "eve", "geldi", "."],
        bio_tags=["B-EMPHASIS", "O", "O", "O"],
        contrastive_pair="Eve Ali geldi.",
        context_question="Kim eve geldi?"
    )
    
    print("Sample JSON:")
    print(sample.to_json())
    print(f"\nValid: {validate_sample(sample)}")
