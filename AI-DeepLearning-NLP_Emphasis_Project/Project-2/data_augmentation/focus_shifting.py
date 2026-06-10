"""
Focus Shifting Strategy (Strategy A)
Generates emphasis variations by changing word order
"""
import random
from typing import List, Tuple
from schema import EmphasisSample, create_bio_tags, FOCUS_TYPES
import uuid


class FocusShifter:
    """Generate emphasis variations by shifting focus to different sentence elements"""
    
    def __init__(self):
        # Turkish sentence element patterns (SOV language)
        self.element_roles = {
            "subject": ["ben", "sen", "o", "biz", "siz", "onlar", "ali", "ayşe", "mehmet", "anne", "baba"],
            "time": ["yarın", "bugün", "dün", "akşam", "sabah", "gece", "bu yıl", "geçen hafta"],
            "location": ["eve", "okula", "işe", "markete", "parka", "hastaneye", "ankara'ya", "istanbul'a"],
            "object": ["kitabı", "arabayı", "suyu", "yemeği", "ödevi", "mektubu"],
            "manner": ["hızlı", "yavaş", "dikkatli", "sessiz", "koşarak", "yürüyerek"]
        }
        
        self.context_questions = {
            "subject": ["Kim?", "Kimler?"],
            "object": ["Neyi?", "Kimi?"],
            "time": ["Ne zaman?", "Hangi gün?"],
            "location": ["Nereye?", "Nerede?"],
            "manner": ["Nasıl?", "Ne şekilde?"]
        }
    
    def detect_role(self, token: str) -> str:
        """Detect the grammatical role of a token"""
        token_lower = token.lower().rstrip('.,!?')
        
        for role, words in self.element_roles.items():
            if any(word in token_lower for word in words):
                return role
        
        # Morphological hints
        if token_lower.endswith(('ı', 'i', 'u', 'ü', 'yı', 'yi')):
            return "object"  # Accusative case
        elif token_lower.endswith(('e', 'a', 'ye', 'ya')):
            return "location"  # Dative case
        elif token_lower.endswith(('de', 'da', 'te', 'ta')):
            return "location"  # Locative case
        elif token_lower.endswith(('le', 'la', 'yle', 'yla')):
            return "manner"  # Instrumental case
        
        return "unknown"
    
    def generate_variations(self, sentence: str, tokens: List[str]) -> List[EmphasisSample]:
        """Generate focus-shifted variations of a sentence"""
        variations = []
        
        # Identify roles for each token
        token_roles = [(token, self.detect_role(token)) for token in tokens]
        
        # Generate variations for each identifiable element
        for i, (token, role) in enumerate(token_roles):
            if role == "unknown":
                continue
            
            # Create focus on this token
            focus_type = f"{role.upper()}_FOCUS"
            bio_tags = ["O"] * len(tokens)
            bio_tags[i] = "B-EMPHASIS"
            
            # Generate contrastive pair by moving focused element
            contrastive_tokens = tokens.copy()
            if i > 0:
                # Move focused element to beginning
                contrastive_tokens.insert(0, contrastive_tokens.pop(i))
                contrastive_sentence = " ".join(contrastive_tokens)
            else:
                # Move to end (before verb)
                verb_idx = len(contrastive_tokens) - 2  # Assuming last is punctuation
                if verb_idx > 0:
                    contrastive_tokens.insert(verb_idx, contrastive_tokens.pop(i))
                contrastive_sentence = " ".join(contrastive_tokens)
            
            # Get context question
            questions = self.context_questions.get(role, ["?"])
            context_q = random.choice(questions)
            
            sample = EmphasisSample(
                id=str(uuid.uuid4())[:8],
                sentence=sentence,
                focus_token=token,
                focus_type=focus_type,
                tokens=tokens,
                bio_tags=bio_tags,
                contrastive_pair=contrastive_sentence,
                context_question=context_q,
                source="focus_shifting"
            )
            variations.append(sample)
        
        return variations
    
    def augment_dataset(self, sentences: List[str]) -> List[EmphasisSample]:
        """Augment a list of sentences with focus-shifted variations"""
        all_samples = []
        
        for sentence in sentences:
            tokens = sentence.replace('.', ' .').replace(',', ' ,').split()
            variations = self.generate_variations(sentence, tokens)
            all_samples.extend(variations)
        
        print(f"✓ Generated {len(all_samples)} focus-shifted samples from {len(sentences)} sentences")
        return all_samples


# Pre-defined base sentences for augmentation
BASE_SENTENCES = [
    "Ali yarın okula gidecek.",
    "Ayşe dün kitabı okudu.",
    "Ben bugün markete gittim.",
    "Annem akşam yemeği hazırladı.",
    "Öğrenciler sabah derse girdi.",
    "Mehmet hızlı koşarak eve geldi.",
    "Biz geçen hafta Ankara'ya gittik.",
    "Çocuklar parkta oyun oynadı.",
    "Doktor hastaya ilaç verdi.",
    "Öğretmen öğrencilere soru sordu.",
]


if __name__ == "__main__":
    shifter = FocusShifter()
    
    # Test with base sentences
    samples = shifter.augment_dataset(BASE_SENTENCES)
    
    print(f"\nGenerated {len(samples)} samples:")
    for sample in samples[:5]:
        print(f"\n  Sentence: {sample.sentence}")
        print(f"  Focus: {sample.focus_token} ({sample.focus_type})")
        print(f"  Tags: {sample.bio_tags}")
        print(f"  Question: {sample.context_question}")
        print(f"  Contrastive: {sample.contrastive_pair}")
