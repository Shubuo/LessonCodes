import pandas as pd
import random

class TurkishEmphasisGenerator:
    def __init__(self):
        #  veri setindeki mantiğa dayali bağlam sorulari şablonlari.
        # Bu şablonlar, vurgunun "contrastive" (zitlik) doğasini ortaya çikarir.
        self.context_templates = {
            "subject": [
                "Kim yaptı?",
                "Özne kim?",
                "Konu kim/ne?"
            ],
            "object": [
                "Neyi etkilendi?", 
                "Nesne olarak ne seçildi?", 
                "Hangi şeyi?"
            ],
            "time": [
                "Ne zaman oldu?", 
                "Hangi gün gerçekleşecek?", 
                "Zamanlamasi neydi?"
            ],
            "location": [
                "Nerede oldu?", 
                "Nereye gidiliyor?", 
                "Konumu neresi?"
            ],
            "manner": [
                "Nasil yapildi?", 
                "Hangi araçla?", 
                "Hangi yöntemle?"
            ],
            "verb": [
                "Ne yapti?", 
                "Olay nedir?", 
                "Eylem gerçekleşti mi?"
            ]
        }

    def detect_role_heuristic(self, sentence, emphasized_word):
        """
        Vurgulanan kelimenin cümredeki rolünü (Özne, Nesne, Yer vb.) 
        basit morfolojik kurallarla tahmin eder.
        Gerçek uygulamada bir Dependency Parser (örn. Stanza) kullanilmalidir.
        """
        word = emphasized_word.lower()
        
        # Basit sezgisel kurallar (Heuristics)
        if word in ["ben", "sen", "o", "biz", "siz", "onlar", "ali", "ayşe", "annem"]:
            return "subject"
        elif any(x in word for x in ["dün", "yarin", "bugün", "akşam", "sabah"]):
            return "time"
        elif word.endswith(("de", "da", "te", "ta")): # Locative
            return "location"
        elif word.endswith(("e", "a", "ye", "ya")): # Dative (Yönelme) -> Genellikle Yer veya Nesne
            return "location" 
        elif word.endswith(("i", "i", "u", "ü", "yi", "yi", "yu", "yü")): # Accusative (Belirtme)
            return "object"
        elif word.endswith(("le", "la")): # Instrumental (Vasita)
            return "manner"
        else:
            # Varsayilan olarak fiil veya belirsiz
            return "verb"

    def create_instruction_data(self, row):
        """
         formatindaki bir satiri, LLM eğitimi için 'Instruction Tuning' formatina çevirir.
        """
        sentence = row['sentence'] if isinstance(row, dict) else row.iloc[0]
        emph_word = row['emphasized_word'] if isinstance(row, dict) else row.iloc[1]
        explanation = row['explanation'] if isinstance(row, dict) else row.iloc[2]
        
        role = self.detect_role_heuristic(sentence, emph_word)
        question = random.choice(self.context_templates.get(role, ["Ne anlama geliyor?"]))
        
        # LLM için Prompt (Girdi) 
        prompt = f"""Görev: Aşağidaki cümlede pragmatik vurguyu analiz et.
Bağlam Sorusu: {question}
Cümle: {sentence}

Analiz:"""

        # LLM için Completion (Hedef Çikti)
        completion = f"""Vurgulanan Öge: {emph_word}
Vurgu Türü: {role.upper()}_FOCUS
Pragmatik Anlam: {explanation}
Çikarim: Bu cümle, '{emph_word}' dişindaki alternatifleri (örneğin başka bir zamani, kişiyi veya yeri) reddeder."""

        return {"prompt": prompt, "completion": completion}

# Örnek Kullanım: Veri Yükleme ve Instruction Tuning Formatına Dönüştürme
if __name__ == "__main__":
    import json
    from pathlib import Path
    
    # Load processed data
    data_path = Path(__file__).parent / "data" / "processed" / "train.json"
    
    if data_path.exists():
        with open(data_path, 'r', encoding='utf-8') as f:
            processed_data = json.load(f)
        
        print(f"✓ Loaded {len(processed_data)} training examples")
        
        generator = TurkishEmphasisGenerator()
        
        # Convert first 10 examples to instruction format
        instruction_data = []
        for example in processed_data[:10]:
            # Create a row-like dict for compatibility
            row = {
                'sentence': example['sentence'],
                'emphasized_word': ' '.join([w for w, l in zip(example['words'], example['bio_labels']) 
                                            if l.startswith('B-') or l.startswith('I-')]),
                'explanation': f"Bu cümlede '{example['sentence']}' vurgulanmıştır."
            }
            instruction_data.append(generator.create_instruction_data(row))
        
        # Print sample outputs
        print(f"\n📝 INSTRUCTION TUNING FORMAT EXAMPLES (First 3):\n")
        for i, item in enumerate(instruction_data[:3], 1):
            print(f"{'='*60}")
            print(f"Example {i}:")
            print(f"--- Prompt ---\n{item['prompt']}\n")
            print(f"--- Target Completion ---\n{item['completion']}\n")
        
        # Save instruction tuning dataset
        output_path = Path(__file__).parent / "data" / "processed" / "instruction_tuning_train.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert all training data
        all_instruction_data = []
        for example in processed_data:
            row = {
                'sentence': example['sentence'],
                'emphasized_word': ' '.join([w for w, l in zip(example['words'], example['bio_labels']) 
                                            if l.startswith('B-') or l.startswith('I-')]),
                'explanation': f"Vurgu analizi"
            }
            all_instruction_data.append(generator.create_instruction_data(row))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_instruction_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Saved {len(all_instruction_data)} instruction examples to {output_path.name}")
    else:
        print(f"❌ Data file not found: {data_path}")
        print(f"   Please run 'python data_loader.py' first to process the legacy datasets.")