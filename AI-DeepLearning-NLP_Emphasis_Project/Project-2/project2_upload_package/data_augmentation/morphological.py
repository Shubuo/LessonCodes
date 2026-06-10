"""
Morphological Variation Strategy (Strategy C)
Generates emphasis changes using Turkish morphological markers
"""
import random
from typing import List, Tuple
from schema import EmphasisSample
import uuid


class MorphologicalAugmenter:
    """Generate emphasis variations using Turkish morphological markers"""
    
    def __init__(self):
        # Emphasis-changing suffixes in Turkish
        self.emphasis_particles = {
            "question": ["-mi", "-mı", "-mu", "-mü"],  # Question particle
            "negation": ["-me", "-ma"],  # Negation
            "certainty": ["-DIr", "-dir", "-dır", "-dur", "-dür"],  # Certainty/assertion
            "focus": ["-de", "-da", "-te", "-ta"],  # Also/even (focus particle)
            "only": ["sadece", "yalnızca", "tek"]  # Only (pre-word focus)
        }
        
        # Verb stem patterns for morphological changes
        self.verb_patterns = {
            "past": ("dı", "di", "du", "dü", "tı", "ti", "tu", "tü"),
            "future": ("ecek", "acak"),
            "present": ("yor", "iyor", "uyor", "üyor")
        }
    
    def add_question_particle(self, sentence: str, focus_word: str) -> Tuple[str, str, List[str]]:
        """Add question particle after focus word to emphasize it"""
        words = sentence.split()
        new_words = []
        focus_idx = -1
        
        for i, word in enumerate(words):
            new_words.append(word)
            if focus_word.lower() in word.lower():
                # Determine vowel harmony
                last_vowel = self._get_last_vowel(word)
                particle = self._get_question_particle(last_vowel)
                new_words.append(particle)
                focus_idx = i
        
        if focus_idx >= 0:
            bio_tags = ["O"] * len(new_words)
            bio_tags[focus_idx] = "B-EMPHASIS"
            return " ".join(new_words), focus_word, bio_tags
        
        return sentence, focus_word, ["O"] * len(words)
    
    def add_focus_particle(self, sentence: str, focus_word: str) -> Tuple[str, str, List[str]]:
        """Add 'de/da' focus particle to emphasize a word"""
        words = sentence.split()
        new_words = []
        focus_idx = -1
        
        for i, word in enumerate(words):
            if focus_word.lower() in word.lower():
                # Add 'de/da' after the word
                last_vowel = self._get_last_vowel(word)
                particle = "de" if last_vowel in "eiöü" else "da"
                new_words.append(f"{word} {particle}")
                focus_idx = len(new_words) - 1
            else:
                new_words.append(word)
        
        bio_tags = ["O"] * len(new_words)
        if focus_idx >= 0:
            bio_tags[focus_idx] = "B-EMPHASIS"
        
        return " ".join(new_words), focus_word, bio_tags
    
    def add_only_prefix(self, sentence: str, focus_word: str) -> Tuple[str, str, List[str]]:
        """Add 'sadece/yalnızca' before focus word"""
        words = sentence.split()
        new_words = []
        focus_indices = []
        
        prefix = random.choice(["sadece", "yalnızca"])
        
        for i, word in enumerate(words):
            if focus_word.lower() in word.lower():
                new_words.append(prefix)
                new_words.append(word)
                focus_indices = [len(new_words) - 2, len(new_words) - 1]
            else:
                new_words.append(word)
        
        bio_tags = ["O"] * len(new_words)
        if focus_indices:
            bio_tags[focus_indices[0]] = "B-EMPHASIS"
            bio_tags[focus_indices[1]] = "I-EMPHASIS"  # Multi-word emphasis!
        
        return " ".join(new_words), f"{prefix} {focus_word}", bio_tags
    
    def negate_verb(self, sentence: str) -> Tuple[str, str, List[str]]:
        """Negate the verb to create emphasis on negation"""
        words = sentence.split()
        new_words = []
        verb_idx = -1
        
        for i, word in enumerate(words):
            # Check if word is a verb (ends with tense markers)
            is_verb = any(word.lower().endswith(end) for ends in self.verb_patterns.values() for end in ends)
            
            if is_verb and verb_idx < 0:
                # Insert negation
                negated = self._negate_verb(word)
                new_words.append(negated)
                verb_idx = i
            else:
                new_words.append(word)
        
        bio_tags = ["O"] * len(new_words)
        if verb_idx >= 0:
            bio_tags[verb_idx] = "B-EMPHASIS"
        
        return " ".join(new_words), new_words[verb_idx] if verb_idx >= 0 else "", bio_tags
    
    def _get_last_vowel(self, word: str) -> str:
        """Get the last vowel in a word for harmony"""
        vowels = "aeıioöuü"
        for char in reversed(word.lower()):
            if char in vowels:
                return char
        return "a"
    
    def _get_question_particle(self, last_vowel: str) -> str:
        """Get appropriate question particle based on vowel harmony"""
        if last_vowel in "eii":
            return "mi"
        elif last_vowel in "aı":
            return "mı"
        elif last_vowel in "ouu":
            return "mu"
        else:  # öü
            return "mü"
    
    def _negate_verb(self, verb: str) -> str:
        """Simple verb negation (basic implementation)"""
        # This is simplified - real Turkish morphology is more complex
        for tense, endings in self.verb_patterns.items():
            for end in endings:
                if verb.lower().endswith(end):
                    stem = verb[:-len(end)]
                    vowel = self._get_last_vowel(stem)
                    neg = "me" if vowel in "eiöü" else "ma"
                    return stem + neg + end
        return verb
    
    def augment_sample(self, sample: EmphasisSample) -> List[EmphasisSample]:
        """Generate morphological variations of a sample"""
        variations = []
        
        # 1. Question particle variation
        new_sent, focus, tags = self.add_question_particle(sample.sentence, sample.focus_token)
        if new_sent != sample.sentence:
            variations.append(EmphasisSample(
                id=str(uuid.uuid4())[:8],
                sentence=new_sent,
                focus_token=focus,
                focus_type=sample.focus_type,
                tokens=new_sent.split(),
                bio_tags=tags,
                contrastive_pair=sample.sentence,
                context_question=sample.context_question,
                source="morphological_question"
            ))
        
        # 2. Focus particle variation (de/da)
        new_sent, focus, tags = self.add_focus_particle(sample.sentence, sample.focus_token)
        if new_sent != sample.sentence:
            variations.append(EmphasisSample(
                id=str(uuid.uuid4())[:8],
                sentence=new_sent,
                focus_token=focus,
                focus_type=sample.focus_type,
                tokens=new_sent.split(),
                bio_tags=tags,
                contrastive_pair=sample.sentence,
                context_question=sample.context_question,
                source="morphological_focus"
            ))
        
        # 3. Only prefix variation (creates I-EMPHASIS!)
        new_sent, focus, tags = self.add_only_prefix(sample.sentence, sample.focus_token)
        if "I-EMPHASIS" in tags:
            variations.append(EmphasisSample(
                id=str(uuid.uuid4())[:8],
                sentence=new_sent,
                focus_token=focus,
                focus_type=sample.focus_type,
                tokens=new_sent.split(),
                bio_tags=tags,
                contrastive_pair=sample.sentence,
                context_question=sample.context_question,
                source="morphological_only"
            ))
        
        return variations


if __name__ == "__main__":
    augmenter = MorphologicalAugmenter()
    
    # Test sample
    test_sample = EmphasisSample(
        id="test_001",
        sentence="Ali yarın okula gidecek.",
        focus_token="yarın",
        focus_type="TIME_FOCUS",
        tokens=["Ali", "yarın", "okula", "gidecek."],
        bio_tags=["O", "B-EMPHASIS", "O", "O"],
        context_question="Ne zaman?"
    )
    
    variations = augmenter.augment_sample(test_sample)
    
    print(f"Generated {len(variations)} morphological variations:\n")
    for var in variations:
        print(f"  Source: {var.source}")
        print(f"  Sentence: {var.sentence}")
        print(f"  Focus: {var.focus_token}")
        print(f"  Tags: {var.bio_tags}")
        print()
