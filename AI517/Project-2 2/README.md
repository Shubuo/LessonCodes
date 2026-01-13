# Turkish Stress Detection - LLM Token Classification

🇹🇷 Türkçe cümlelerde vurgu tespiti için BERTurk tabanlı token sınıflandırma modeli.

## 📊 Proje Özeti

Bu proje, Türkçe cümlelerdeki pragmatik vurguyu tespit etmek için **LLM tabanlı token sınıflandırma** kullanmaktadır.

### Performans Metrikleri
- **Accuracy**: 79.7%
- **F1 Score**: 74.9%
- **Precision**: 78.5%
- **Recall**: 79.7%

### Veri Seti
- **Toplam**: 6,253 örnek (25,212 kelime)
- **Train**: 4,377 örnek
- **Validation**: 938 örnek  
- **Test**: 938 örnek
- **Kaynak**: `vurgu_varyasyonlari.csv` (4,304) + `vurguHece.csv` (1,949)

## 🚀 Kurulum

### Gereksinimler
```bash
conda create -n turkish-stress python=3.10
conda activate turkish-stress

pip install transformers torch datasets pandas scikit-learn matplotlib seaborn beautifulsoup4 lxml
```

### Veri Hazırlama
```bash
# Legacy CSV dosyalarını yerleştirin:
# - legacy/vurgu_varyasyonlari.csv
# - legacy/vurguHece.csv

# Veriyi işleyin
python data_loader.py
```

## 🏋️ Model Eğitimi

```bash
# Tam pipeline (veri + eğitim + değerlendirme + görselleştirme)
python run_pipeline.py

# Veya adım adım:
python run_pipeline.py data        # Sadece veri işleme
python token-classification.py     # Sadece eğitim
python evaluation.py               # Sadece değerlendirme
python visualize.py               # Sadece görselleştirme
```

### Eğitim Ayarları
- **Model**: `dbmdz/bert-base-turkish-cased`
- **Batch Size**: 8 (gradient accumulation: 2)
- **Epochs**: 3
- **Learning Rate**: 2e-5
- **Hardware**: CPU (Mac)

## 🔍 Kullanım

### Inference (Yeni Cümle)
```bash
python token-classification.py --predict "Yarın okula gideceğim"
```

**Çıktı:**
```
Original: Yarın okula gideceğim
Words: ['Yarın', 'okula', 'gideceğim']
Labels: ['O', 'O', 'O']
Highlighted: Yarın okula gideceğim
```

### Vurgulu Örnek
```python
# Beklenen: "**Ben** yarın okula gideceğim" (özne vurgusu)
python token-classification.py --predict "Ben yarın okula gideceğim"
```

## 📁 Proje Yapısı

```
Project-2/
├── config.py                    # Merkezi konfigürasyon
├── data_loader.py               # CSV → BIO format dönüştürme
├── sentetic-data.py             # Instruction tuning veri üretimi
├── token-classification.py      # Model eğitim ve inference
├── evaluation.py                # Değerlendirme ve confusion matrix
├── visualize.py                 # Görselleştirmeler
├── run_pipeline.py              # Tam workflow orchestration
│
├── data/
│   └── processed/               # İşlenmiş train/val/test JSON
│
├── outputs/
│   ├── checkpoints/             # Eğitilmiş model (GİT'E EKLENMEDİ)
│   ├── results/                 # Evaluation sonuçları
│   │   ├── confusion_matrix.png
│   │   ├── evaluation_metrics.json
│   │   └── per_class_metrics.csv
│   └── figures/                 # Görselleştirmeler
│
└── legacy/                      # Orijinal CSV dosyaları
    ├── vurgu_varyasyonlari.csv
    └── vurguHece.csv
```

## 📥 Model İndirme

**ÖNEMLİ**: Eğitilmiş model dosyaları (~440MB) GitHub'a yüklenmemiştir.

### Seçenek 1: Modeli Kendiniz Eğitin
```bash
python run_pipeline.py
# Model otomatik olarak outputs/checkpoints/ klasörüne kaydedilir
```

### Seçenek 2: Önceden Eğitilmiş Modeli İndirin
```bash
# Google Drive model indirilecek (link eklenecek)
# Model'i sıkıştır
# wget https://...model.tar.gz
# tar -xzf model.tar.gz -C outputs/checkpoints/

### Seçenek 2: Hugging Face Hub (Önerilen)
pip install huggingface_hub

# Model'i HF'ye yükle
python -c "
from huggingface_hub import HfApi
api = HfApi()
api.upload_folder(
    folder_path='outputs/checkpoints',
    repo_id='USERNAME/turkish-stress-berturk',
    repo_type='model'
)
"
```
README'de:
```markdown
## Model İndirme
\`\`\`bash
pip install huggingface_hub
huggingface-cli download USERNAME/turkish-stress-berturk --local-dir outputs/checkpoints
\`\`\`
```


## 📊 Sonuçlar

### Per-Class Performance

| Label | Precision | Recall | F1 Score | Support |
|-------|-----------|--------|----------|---------|
| **O** (No Emphasis) | 80.6% | 99.1% | 88.9% | 3,023 |
| **B-EMPHASIS** (Begin) | 71.9% | 9.0% | 16.0% | 765 |
| **I-EMPHASIS** (Inside) | 0.0% | 0.0% | 0.0% | 27 |
| **Weighted Avg** | 78.2% | 80.3% | 73.6% | 3,815 |

### Ana Bulgular
✅ Vurgusuz kelimeleri yüksek doğrulukla tespit eder (99% recall)  
⚠️ Vurgu başlangıcını orta seviyede tespit eder (71.9% precision, düşük recall)  
❌ Çok kelimeli vurgu kalıplarında zorlanır (I-EMPHASIS: %0.2 veri)

## 🛠️ Geliştirme Alanları

1. **Veri Dengeleme**: B-EMPHASIS ve I-EMPHASIS için oversampling
2. **Büyük Modeller**: `savasy/bert-base-turkish-sentiment`, `loodos/bert-turkish` dene
3. **Weighted Loss**: Class imbalance için ağırlıklı loss fonksiyonu
4. **Contrastive Learning**: "Ali okula gitti" vs "Okula Ali gitti" çiftleri
5. **CRF Layer**: Dizi tahminleri için Conditional Random Field ekle

## 📚 Kaynaklar

- **v1 (NMT) Yaklaşımı**: `legacy/` klasöründeki Jupyter notebook'lar
- **Veri Üretimi**: Gemini API ile sentetik veri (help.py, sela.py)
- **BERTurk Model**: [dbmdz/bert-base-turkish-cased](https://huggingface.co/dbmdz/bert-base-turkish-cased)

## 👥 Katkıda Bulunanlar
Burak YORUK
Egemen KACIKAN
Berken CAM

---

**Not**: Eğitilmiş model dosyaları büyük olduğu için Git'e dahil edilmemiştir. Modeli kendiniz eğitebilir veya paylaşılan linkten indirebilirsiniz.
