"""
Data Loader for Turkish Stress Detection
Loads and processes legacy CSV datasets, converts to token classification format
"""
import pandas as pd
import numpy as np
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from sklearn.model_selection import train_test_split
from bs4 import BeautifulSoup
from collections import Counter
import config

class TurkishStressDataLoader:
    """Load and process Turkish stress detection datasets"""
    
    def __init__(self):
        self.label2id = config.LABEL2ID
        self.id2label = config.ID2LABEL
        self.train_data = []
        self.val_data = []
        self.test_data = []
        
    def extract_emphasis_from_html(self, sentence: str) -> Tuple[str, List[str], List[int]]:
        """
        Extract emphasized words from HTML tagged sentence
        
        Args:
            sentence: HTML string like "Yarin <em>okula</em> gideceğim"
            
        Returns:
            clean_text: Text without HTML tags
            words: List of words
            labels: List of word-level labels (0=no emphasis, 1=emphasis)
        """
        # Parse HTML
        soup = BeautifulSoup(sentence, 'html.parser')
        
        # Get all text and emphasized text
        clean_text = soup.get_text()
        emphasized_words = [em.get_text() for em in soup.find_all('em')]
        
        # Split into words (simple tokenization)
        words = clean_text.split()
        
        # Create word-level labels
        labels = []
        for word in words:
            # Check if this word or part of it is emphasized
            is_emphasized = any(emph.lower() in word.lower() for emph in emphasized_words)
            labels.append(1 if is_emphasized else 0)
            
        return clean_text, words, labels
    
    def load_vurgu_varyasyonlari(self) -> List[Dict]:
        """Load word-level emphasis dataset (vurgu_varyasyonlari.csv)"""
        print(f"\n📁 Loading {config.VURGU_VARYASYONLARI_PATH.name}...")
        
        try:
            # Try reading with different encodings and handle errors
            for encoding in ['utf-8', 'latin1', 'iso-8859-9']:
                try:
                    # Read with error handling for malformed rows
                    df = pd.read_csv(
                        config.VURGU_VARYASYONLARI_PATH, 
                        encoding=encoding,
                        on_bad_lines='skip',  # Skip malformed lines
                        quoting=1,  # QUOTE_ALL
                        escapechar='\\'
                    )
                    break
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            
            print(f"  ✓ Loaded {len(df)} examples")
            print(f"  Columns: {list(df.columns)}")
            
            # Process each row
            examples = []
            for idx, row in df.iterrows():
                try:
                    # Get sentence (first column is usually the sentence)
                    sentence = str(row.iloc[0])
                    
                    # Skip if sentence is empty or NaN
                    if pd.isna(sentence) or sentence.strip() == '':
                        continue
                    
                    # Extract emphasis information
                    clean_text, words, labels = self.extract_emphasis_from_html(sentence)
                    
                    # Skip if no words extracted
                    if len(words) == 0:
                        continue
                    
                    # Get focus type if available (second column)
                    focus_type = str(row.iloc[1]) if len(row) > 1 and not pd.isna(row.iloc[1]) else "unknown"
                    
                    examples.append({
                        'id': f'var_{idx}',
                        'sentence': clean_text,
                        'words': words,
                        'labels': labels,
                        'focus_type': focus_type,
                        'source': 'vurgu_varyasyonlari'
                    })
                except Exception as e:
                    # Skip problematic rows
                    continue
                
            print(f"  ✓ Processed {len(examples)} valid examples")
            return examples
            
        except Exception as e:
            print(f"  ✗ Error loading file: {e}")
            return []
    
    def load_vurgu_hece(self) -> List[Dict]:
        """Load syllable-level emphasis dataset (vurguHece.csv)"""
        print(f"\n📁 Loading {config.VURGU_HECE_PATH.name}...")
        
        try:
            # Try reading with different encodings and handle errors
            for encoding in ['utf-8', 'latin1', 'iso-8859-9']:
                try:
                    df = pd.read_csv(
                        config.VURGU_HECE_PATH,
                        encoding=encoding,
                        on_bad_lines='skip',  # Skip malformed lines
                        quoting=1,  # QUOTE_ALL
                        escapechar='\\'
                    )
                    break
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            
            print(f"  ✓ Loaded {len(df)} examples")
            print(f"  Columns: {list(df.columns)}")
            
            # Process each row
            examples = []
            for idx, row in df.iterrows():
                try:
                    # Get sentence (first column)
                    sentence = str(row.iloc[0])
                    
                    # Skip if sentence is empty or NaN
                    if pd.isna(sentence) or sentence.strip() == '':
                        continue
                    
                    # Extract emphasis information
                    clean_text, words, labels = self.extract_emphasis_from_html(sentence)
                    
                    # Skip if no words extracted
                    if len(words) == 0:
                        continue
                    
                    # Get additional info if available
                    emphasized_word = str(row.iloc[1]) if len(row) > 1 and not pd.isna(row.iloc[1]) else ""
                    explanation = str(row.iloc[4]) if len(row) > 4 and not pd.isna(row.iloc[4]) else ""
                    
                    examples.append({
                        'id': f'hece_{idx}',
                        'sentence': clean_text,
                        'words': words,
                        'labels': labels,
                        'emphasized_word': emphasized_word,
                        'explanation': explanation,
                        'source': 'vurguHece'
                    })
                except Exception as e:
                    # Skip problematic rows
                    continue
                
            print(f"  ✓ Processed {len(examples)} valid examples")
            return examples
            
        except Exception as e:
            print(f"  ✗ Error loading file: {e}")
            return []
    
    def convert_to_bio_format(self, words: List[str], labels: List[int]) -> List[str]:
        """
        Convert binary labels to BIO format
        
        Args:
            words: List of words
            labels: Binary labels (0=no emphasis, 1=emphasis)
            
        Returns:
            BIO labels: ['O', 'B-EMPHASIS', 'I-EMPHASIS', ...]
        """
        bio_labels = []
        in_emphasis = False
        
        for i, label in enumerate(labels):
            if label == 1:
                if not in_emphasis:
                    bio_labels.append('B-EMPHASIS')
                    in_emphasis = True
                else:
                    bio_labels.append('I-EMPHASIS')
            else:
                bio_labels.append('O')
                in_emphasis = False
                
        return bio_labels
    
    def load_all_data(self) -> List[Dict]:
        """Load all datasets and combine"""
        print("\n" + "="*60)
        print("📚 LOADING TURKISH STRESS DETECTION DATASETS")
        print("="*60)
        
        all_examples = []
        
        # Load both datasets
        vurgu_var_examples = self.load_vurgu_varyasyonlari()
        vurgu_hece_examples = self.load_vurgu_hece()
        
        all_examples.extend(vurgu_var_examples)
        all_examples.extend(vurgu_hece_examples)
        
        print(f"\n📊 DATASET STATISTICS")
        print(f"  Total examples: {len(all_examples)}")
        print(f"  From vurgu_varyasyonlari: {len(vurgu_var_examples)}")
        print(f"  From vurguHece: {len(vurgu_hece_examples)}")
        
        # Count emphasized vs non-emphasized
        total_words = sum(len(ex['words']) for ex in all_examples)
        emphasized_words = sum(sum(ex['labels']) for ex in all_examples)
        print(f"  Total words: {total_words}")
        if total_words > 0:
            print(f"  Emphasized words: {emphasized_words} ({emphasized_words/total_words*100:.1f}%)")
        else:
            print(f"  Emphasized words: {emphasized_words}")
        
        return all_examples
    
    def split_data(self, examples: List[Dict], 
                   train_ratio: float = config.TRAIN_RATIO,
                   val_ratio: float = config.VAL_RATIO,
                   test_ratio: float = config.TEST_RATIO,
                   random_seed: int = config.RANDOM_SEED):
        """Split data into train/val/test sets"""
        
        print(f"\n✂️  SPLITTING DATA")
        print(f"  Train: {train_ratio*100:.0f}%, Val: {val_ratio*100:.0f}%, Test: {test_ratio*100:.0f}%")
        
        # First split: train vs (val + test)
        train_data, temp_data = train_test_split(
            examples, 
            test_size=(val_ratio + test_ratio),
            random_state=random_seed
        )
        
        # Second split: val vs test
        val_ratio_adjusted = val_ratio / (val_ratio + test_ratio)
        val_data, test_data = train_test_split(
            temp_data,
            test_size=(1 - val_ratio_adjusted),
            random_state=random_seed
        )
        
        self.train_data = train_data
        self.val_data = val_data
        self.test_data = test_data
        
        print(f"  ✓ Train: {len(train_data)} examples")
        print(f"  ✓ Val: {len(val_data)} examples")
        print(f"  ✓ Test: {len(test_data)} examples")
        
        return train_data, val_data, test_data
    
    def save_processed_data(self):
        """Save processed data to JSON files"""
        print(f"\n💾 SAVING PROCESSED DATA")
        
        for split_name, split_data in [('train', self.train_data), 
                                        ('val', self.val_data), 
                                        ('test', self.test_data)]:
            output_path = config.PROCESSED_DIR / f"{split_name}.json"
            
            # Convert to JSON-serializable format
            processed_examples = []
            for ex in split_data:
                bio_labels = self.convert_to_bio_format(ex['words'], ex['labels'])
                processed_examples.append({
                    'id': ex['id'],
                    'sentence': ex['sentence'],
                    'words': ex['words'],
                    'bio_labels': bio_labels,
                    'label_ids': [self.label2id[label] for label in bio_labels],
                    'source': ex['source']
                })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_examples, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ Saved {len(processed_examples)} examples to {output_path.name}")
        
        print(f"\n✅ Data processing complete!")
        print(f"  Processed data saved to: {config.PROCESSED_DIR}")
    
    def print_sample_examples(self, n=3):
        """Print sample examples from training data"""
        print(f"\n📝 SAMPLE EXAMPLES (First {n} from training set)")
        print("="*60)
        
        for i, ex in enumerate(self.train_data[:n], 1):
            bio_labels = self.convert_to_bio_format(ex['words'], ex['labels'])
            print(f"\nExample {i}:")
            print(f"  Sentence: {ex['sentence']}")
            print(f"  Words: {ex['words']}")
            print(f"  Labels: {bio_labels}")
            
            # Highlight emphasized words
            highlighted = []
            for word, label in zip(ex['words'], bio_labels):
                if label.startswith('B-') or label.startswith('I-'):
                    highlighted.append(f"**{word}**")
                else:
                    highlighted.append(word)
            print(f"  Highlighted: {' '.join(highlighted)}")


def main():
    """Main function to load and process data"""
    loader = TurkishStressDataLoader()
    
    # Load all data
    all_examples = loader.load_all_data()
    
    if len(all_examples) == 0:
        print("\n❌ No data loaded! Check if CSV files exist and are readable.")
        return
    
    # Split data
    loader.split_data(all_examples)
    
    # Print sample examples
    loader.print_sample_examples(n=5)
    
    # Save processed data
    loader.save_processed_data()
    
    print("\n" + "="*60)
    print("🎉 SUCCESS! Data is ready for model training.")
    print("="*60)


if __name__ == "__main__":
    main()
