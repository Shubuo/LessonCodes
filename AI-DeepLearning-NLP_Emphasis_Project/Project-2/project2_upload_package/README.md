# 🇹🇷 Turkish Stress Detection - BERTurk + CRF

Türkçe cümlelerde pragmatik vurgu tespiti için **BERTurk + CRF** tabanlı token sınıflandırma modeli.

> **AI517**  dersi kapsamında geliştirilmiştir.

---

## 📊 Proje Özeti

Bu proje, Türkçe cümlelerdeki pragmatik vurguyu tespit etmek için **LLM tabanlı token sınıflandırma** kullanmaktadır.

### 🎯 v3 Performans Metrikleri

| Metrik | v1 (Baseline) | v3 (CRF) |
|--------|---------------|----------|
| **Model** | BERTurk | BERTurk + CRF |
| **Test Accuracy** | 79.7% | **100%** |
| **B-EMPHASIS Recall** | 9.0% | **100%** |
| **I-EMPHASIS Recall** | 0.0% | **100%** |
| **Epochs** | 3 | 25 |

### 📁 Veri Seti
- **Toplam**: 6,253 örnek (25,212 kelime)
- **Train**: 4,377 örnek
- **Validation**: 938 örnek  
- **Test**: 938 örnek
- **Format**: BIO (B-EMPHASIS, I-EMPHASIS, O)

---

## ⚠️ Büyük Dosyalar - Google Drive

**Model ve işlenmiş veri dosyaları** (~1.2GB) GitHub'a yüklenmemiştir.

### 📥 Google Drive'dan İndirin:
**🔗 [Google Drive - Proje Dosyaları](https://drive.google.com/drive/folders/1PombO62k6lX5v0T8p-ydWtuQpPO3PAQA?usp=sharing)**

Drive'da bulunan dosyalar:
- `best_model_v3.pt` - Eğitilmiş model (422MB)
- `results_v3.json` - Eğitim sonuçları
- `data/processed/` - İşlenmiş JSON veri setleri

### İndirdikten Sonra:
```bash
# Model dosyasını yerleştirin:
mv best_model_v3.pt outputs/

# İşlenmiş veriyi yerleştirin:
mv processed/ data/
```

---

## 🚀 Kurulum

### Gereksinimler
```bash
conda create -n turkish-stress python=3.10
conda activate turkish-stress

pip install transformers torch datasets pandas scikit-learn matplotlib seaborn beautifulsoup4 lxml pytorch-crf seqeval
```

### Hızlı Başlangıç
```bash
# 1. Repo'yu klonlayın
git clone https://github.com/USERNAME/turkish-stress-detection.git
cd turkish-stress-detection

# 2. Büyük dosyaları Drive'dan indirin (yukarıdaki linke bakın)

# 3. Inference çalıştırın
python -c "
from models.bert_crf import BertCRF
import torch

model = BertCRF()
model.load_state_dict(torch.load('outputs/best_model_v3.pt'))
print('Model yüklendi!')
"
```

---

## 🏋️ Model Eğitimi

### Seçenek 1: Google Colab (Önerilen)
```bash
# Colab notebook'u açın
Turkish_Stress_Detection_v2_Colab.ipynb
```
- GPU: T4 (ücretsiz)
- Süre: ~30-45 dakika

### Seçenek 2: Yerel Eğitim
```bash
# Veri hazırlama
python data_loader.py

# Eğitim (CPU'da yavaş!)
python train_v2.py
```

### Eğitim Parametreleri
| Parametre | Değer |
|-----------|-------|
| Model | `dbmdz/bert-base-turkish-cased` |
| Batch Size | 16 |
| Learning Rate | 2e-5 |
| Epochs | 25 |
| CRF Layer | ✅ |
| Weighted Loss | ✅ |

---

## 🔍 Kullanım

### Inference Demo
```python
from models.bert_crf import BertCRF
from transformers import BertTokenizerFast
import torch

# Model ve tokenizer yükle
model = BertCRF()
model.load_state_dict(torch.load('outputs/best_model_v3.pt'))
tokenizer = BertTokenizerFast.from_pretrained('dbmdz/bert-base-turkish-cased')

# Tahmin
text = "Ali yarın okula gidecek."
# Çıktı: **Ali** yarın okula gidecek.
```

---

## 📁 Proje Yapısı

```
Project-2/
├── config.py                    # Merkezi konfigürasyon
├── data_loader.py               # CSV → BIO format dönüştürme
├── train_v2.py                  # v3 eğitim scripti (CRF)
├── token-classification.py      # v1 eğitim scripti
├── evaluation.py                # Değerlendirme
├── generate_plots.py            # Grafik oluşturma
├── paper.tex                    # IEEE makalesi
├── VIDEO_SCRIPT.md              # Video metni
│
├── data_augmentation/           # Veri artırma modülleri
│   ├── schema.py                # JSONL formatı
│   ├── focus_shifting.py        # Kelime sırası değiştirme
│   ├── morphological.py         # Türkçe ekleri (-mi, -de)
│   └── downsampling.py          # Sınıf dengeleme
│
├── models/                      # Model mimarisi
│   ├── bert_crf.py              # BERTurk + CRF
│   └── weighted_loss.py         # Ağırlıklı kayıp
│
├── outputs/                     # Çıktılar (Drive'dan indir)
│   ├── best_model_v3.pt         # ⬇️ Drive'dan indir
│   ├── results_v3.json
│   └── figures/                 # Görseller
│
├── data/
│   ├── raw/                     # Ham CSV dosyaları
│   └── processed/               # ⬇️ Drive'dan indir
│
└── legacy/                      # v1 NMT yaklaşımı
```

---

## � Teknik Detaylar

### CRF Katmanı
```python
# BIO etiket geçiş kuralları
P(I | O) = -10.0   # O -> I yasak
P(I | B) = +2.0    # B -> I teşvik
Start(I) = -10.0   # Başlangıçta I yasak
```

### Weighted Loss
```
w_c = N_total / (K × N_c)

Ağırlıklar:
- O = 0.42
- B-EMPHASIS = 1.66
- I-EMPHASIS = 47.1
```

---

## 📚 Kaynaklar

- **BERTurk**: [dbmdz/bert-base-turkish-cased](https://huggingface.co/dbmdz/bert-base-turkish-cased)
- **pytorch-crf**: [pytorch-crf.readthedocs.io](https://pytorch-crf.readthedocs.io/)
- **seqeval**: [github.com/chakki-works/seqeval](https://github.com/chakki-works/seqeval)

---

## 👥 Ekip

| İsim | Katkı |
|------|-------|
| **Burak YÖRÜK** | Model geliştirme, veri işleme (%50) |
| **Egemen KAÇIKAN** | Eğitim, değerlendirme (%30) |

---

## 📄 Lisans

Bu proje **AI517 Doğal Dil İşleme** dersi kapsamında geliştirilmiştir.

---

**⭐ Star vermeyi unutmayın!**
