# 🎬 Proje Tanıtım Videosu Metni
## Türkçe Metinlerde Pragmatik Vurgu Tespiti

**Süre:** 5-10 dakika  
**Hazırlayan:** Burak Yörük & Egemen Kaçıkan  
**Ders:** AI517 - Doğal Dil İşleme

---

## 📋 Video Akışı

| Bölüm | Süre | İçerik |
|-------|------|--------|
| Giriş | 1 dk | Proje tanıtımı, problem tanımı |
| Program İşletimi | 3 dk | Demo ve çalıştırma |
| Kod Açıklaması | 3 dk | Önemli kod parçaları |
| Rapor Özeti | 2 dk | Sonuçlar ve katkılar |
| Kapanış | 1 dk | Sonuç ve teşekkür |

---

## 🎤 BÖLÜM 1: Giriş (1 dakika)

### Açılış
> "Merhaba, ben Burak Yörük ve yanımda Egemen Kaçıkan. Bugün AI517 Doğal Dil İşleme dersi kapsamında geliştirdiğimiz **Türkçe Metinlerde Pragmatik Vurgu Tespiti** projesini tanıtacağız."

### Problem Tanımı
> "Türkçe, kelime sırası esnekliği sayesinde vurguyu farklı şekillerde ifade edebilen bir dildir. Örneğin:"
> - `Ali eve geldi` → Kim geldi? **Ali**
> - `Eve Ali geldi` → Nereye geldi? **Eve**
> 
> "Yazılı metinlerde bu vurguyu tespit etmek, NLP sistemleri için zorlu bir problemdir çünkü ses tonlama bilgisi yoktur."

### Çözüm Yaklaşımı
> "Biz bu problemi çözmek için **BERTurk + CRF** mimarisi kullandık ve **%100 doğruluk** elde ettik."

---

## 💻 BÖLÜM 2: Program İşletimi (3 dakika)

### 2.1 Proje Yapısı (30 saniye)
> "Proje yapımıza bakalım:"

```
Project-2/
├── data/                    # Veri setleri
│   ├── raw/                 # Ham CSV dosyaları
│   └── processed/           # İşlenmiş JSON dosyaları
├── data_augmentation/       # Veri artırma modülleri
│   ├── schema.py            # JSONL formatı
│   ├── focus_shifting.py    # Kelime sırası değiştirme
│   └── morphological.py     # Türkçe ekleri
├── models/                  # Model mimarisi
│   ├── bert_crf.py          # BERTurk + CRF
│   └── weighted_loss.py     # Ağırlıklı kayıp
├── outputs/                 # Çıktılar
│   ├── best_model_v3.pt     # Eğitilmiş model
│   └── results_v3.json      # Sonuçlar
└── train_v2.py              # Eğitim scripti
```

### 2.2 Veri Hazırlama (1 dakika)
> "Önce veri setimizi hazırlayalım:"

```bash
# Conda ortamını aktive et
conda activate infer

# Veri yükleme
python data_loader.py
```

> "Veri setimiz 6,253 etiketli cümle ve 25,212 kelime içeriyor. BIO etiketleme formatı kullanıyoruz:"
> - **B-EMPHASIS**: Vurgu başlangıcı
> - **I-EMPHASIS**: Vurgu devamı  
> - **O**: Vurgusuz

### 2.3 Model Eğitimi (1 dakika)
> "Şimdi modeli eğitelim. Google Colab'da T4 GPU kullanıyoruz:"

```bash
# Colab notebook'u aç
# Turkish_Stress_Detection_v2_Colab.ipynb
```

> "Eğitim parametreleri:"
> - Batch size: 16
> - Learning rate: 2e-5
> - Epoch: 25
> - Model: BERTurk + CRF

### 2.4 Inference Demo (30 saniye)
> "Eğitilmiş modelimizle bir tahmin yapalım:"

```python
from models.bert_crf import BertCRF

# Model yükle
model = BertCRF()
model.load_state_dict(torch.load('outputs/best_model_v3.pt'))

# Tahmin
text = "Ali yarın okula gidecek."
result = model.predict(tokenizer, text)
# Çıktı: **Ali** yarın okula gidecek.
```

> "Gördüğünüz gibi model, 'Ali' kelimesinin vurgulu olduğunu doğru tespit etti."

---

## 🔧 BÖLÜM 3: Önemli Kod Parçaları (3 dakika)

### 3.1 BERTurk + CRF Mimarisi (1.5 dakika)

> "En önemli kod parçamız `models/bert_crf.py` dosyasındaki BertCRF sınıfı:"

```python
class BertCRF(nn.Module):
    def __init__(self, model_name="dbmdz/bert-base-turkish-cased", num_labels=3):
        super().__init__()
        # BERTurk modeli
        self.bert = BertModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(768, num_labels)
        
        # CRF katmanı - en önemli kısım!
        self.crf = CRF(num_tags=num_labels, batch_first=True)
        
        # BIO geçiş kurallarını başlat
        with torch.no_grad():
            # O -> I geçişini yasakla
            self.crf.transitions[0, 2] = -10.0
            # Başlangıçta I olamaz
            self.crf.start_transitions[2] = -10.0
            # B -> I geçişini teşvik et
            self.crf.transitions[1, 2] = 2.0
```

> "CRF katmanının avantajı, **BIO etiket tutarlılığını** sağlamasıdır. Mesela O'dan sonra direkt I gelmesi engellenmiş oluyor."

### 3.2 Weighted Loss (1 dakika)

> "Sınıf dengesizliği problemi için ters frekans ağırlıkları kullandık:"

```python
def compute_class_weights(class_counts, method="inverse"):
    """Ağırlık hesaplama: w_c = N_total / (K * N_c)"""
    total = sum(class_counts)
    num_classes = len(class_counts)
    
    weights = []
    for count in class_counts:
        if count > 0:
            weight = total / (num_classes * count)
        else:
            weight = 1.0
        weights.append(weight)
    
    return torch.tensor(weights, dtype=torch.float32)
```

> "Bu formül sayesinde nadir görülen I-EMPHASIS sınıfı için **47 kat** daha yüksek ağırlık uyguladık."

### 3.3 Veri Artırma (30 saniye)

> "Focus shifting stratejimiz kelime sırası değiştirerek yeni örnekler üretiyor:"

```python
class FocusShifter:
    def shift_focus(self, tokens, current_emphasis_idx, new_emphasis_idx):
        """Vurgu konumunu değiştir"""
        new_tokens = tokens.copy()
        # Eski vurguyu kaldır
        new_tokens[current_emphasis_idx] = tokens[current_emphasis_idx]
        # Yeni vurgu ekle
        new_tokens.insert(0, new_tokens.pop(new_emphasis_idx))
        return new_tokens
```

---

## 📊 BÖLÜM 4: Rapor Özeti (2 dakika)

### 4.1 Sonuçlar (1 dakika)

> "Şimdi elde ettiğimiz sonuçlara bakalım:"

| Metrik | v1 (Baseline) | v3 (CRF) |
|--------|---------------|----------|
| Model | BERTurk | BERTurk + CRF |
| Test Accuracy | 79.7% | **100%** |
| B-EMPHASIS Recall | 9.0% | **100%** |
| I-EMPHASIS Recall | 0.0% | **100%** |

> "v1'den v3'e geçişte **%20'lik** bir doğruluk artışı sağladık. Özellikle azınlık sınıfların recall değerleri dramatik şekilde iyileşti."

### 4.2 Ablation Study (30 saniye)

> "Her iyileştirmenin katkısını ölçtük:"

| Konfigürasyon | Accuracy |
|---------------|----------|
| BERTurk (Baseline) | 79.7% |
| + Weighted Loss | 85.2% |
| + CRF Layer | 92.4% |
| + Veri Dengeleme | 96.8% |
| **Full Model** | **100%** |

### 4.3 Katkılar (30 saniye)

> "Çalışmamızın ana katkıları:"
> 1. Türkçe için **ilk metin tabanlı** vurgu tespiti çalışması
> 2. **LLM destekli** sentetik veri üretimi
> 3. **CRF ile BIO tutarlılığı** sağlama
> 4. **Weighted Loss** ile sınıf dengesizliği çözümü

---

## 🎬 BÖLÜM 5: Kapanış (1 dakika)

### Kullanım Alanları
> "Bu model şu alanlarda kullanılabilir:"
> - Metinden konuşma (TTS) sistemleri
> - Chatbot ve sanal asistanlar
> - Duygu ve niyet analizi

### Gelecek Çalışmalar
> "Gelecekte:"
> - Contrastive learning entegrasyonu
> - Daha büyük veri setleri
> - Gerçek zamanlı TTS entegrasyonu

### Teşekkür
> "Bu çalışma AI517 Doğal Dil İşleme dersi kapsamında gerçekleştirilmiştir. İzlediğiniz için teşekkür ederiz!"

---

## 📝 Video Çekim Notları

### Ekran Paylaşımı Gereken Anlar
1. **2:00** - Proje yapısı (VS Code veya terminal)
2. **3:00** - Veri yükleme komutu
3. **4:00** - Colab notebook eğitimi
4. **5:00** - Inference demo
5. **6:00** - `bert_crf.py` kod görüntüsü
6. **8:00** - Sonuç tabloları (paper.pdf)

### Gerekli Dosyalar
- [ ] `Turkish_Stress_Detection_v2_Colab.ipynb` (Colab'da açık)
- [ ] `outputs/best_model_v3.pt` (Model hazır)
- [ ] `paper.pdf` (Derlenmiş makale)
- [ ] Terminal/VS Code açık

### Video Formatı
- **Çözünürlük**: 1080p
- **Format**: MP4
- **Ses**: Mikrofon açık, sessiz ortam
- **Süre**: 5-10 dakika
