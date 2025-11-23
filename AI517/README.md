# Yapay Zeka - 583839 Proje Koleksiyonu

Bu repository, Yapay Zeka dersi (583839) kapsamında geliştirilen makine öğrenmesi projelerini içermektedir.

## 📁 Proje Yapısı

```
Yapay Zeka - 583839/
│
├── README.md                    # Bu dosya
│
├── project1-1/                  # Proje 1.1: Sınıflandırma Analizi
│   └── project1-1.py
│
├── project1-2/                  # Proje 1.2: Kümeleme Analizi
│   └── project1-2.py
│
├── project1-2d/                 # Proje 1.2d: Regresyon Analizi
│   └── project1-2d.py
│
├── 3-derinöğrenme/              # Proje 1.3: Derin Öğrenme
│   ├── project1-3.py            # Ana derin öğrenme kodu (PyTorch)
│   ├── grafik_olustur_simple.py # Grafik oluşturma scripti
│   ├── proje_veri_seti/        # Görüntü veri seti
│   ├── egitim_gecmisi.png      # Eğitim geçmişi grafikleri
│   ├── hata_matrisi.png        # Hata matrisi grafikleri
│   ├── DERIN_OGRENME_ANALIZ_RAPORU.txt
│   ├── VERI_SETI_BILGI.md
│   └── derin_ogrenme_sonucu.txt
│
├── veri_setleri/                # Tüm veri setleri
│   ├── Acoustic Features.csv              # Müzik duygu sınıflandırma
│   ├── reklam_satis_veri_seti.csv         # Reklam-satış regresyon
│   └── turkish+music+emotion.zip          # Orijinal veri seti
│
└── raporlar/                    # Analiz raporları
    ├── analiz_sonucu.txt        # Kümeleme analizi
    └── regresyon_analizi.txt    # Regresyon analizi
```

## 📊 Proje Detayları

### Proje 1.1: Sınıflandırma Analizi

**Klasör:** `project1-1/`  
**Dosya:** `project1-1.py`

- **Veri Seti:** `veri_setleri/Acoustic Features.csv`
- **Yöntemler:** Random Forest, SVM
- **Amaç:** Müzik duygu sınıflandırması (angry, happy, relax, sad)
- **Çalıştırma:**
  ```bash
  cd project1-1
  python project1-1.py
  ```

### Proje 1.2: Kümeleme Analizi

**Klasör:** `project1-2/`  
**Dosya:** `project1-2.py`

- **Veri Seti:** `veri_setleri/Acoustic Features.csv`
- **Yöntemler:** K-Means, Agglomerative Clustering
- **Metrikler:** Adjusted Rand Index (ARI), Silhouette Score
- **Sonuç:** Her iki yöntem de düşük-orta seviyede başarı (%28 ARI)
- **Çalıştırma:**
  ```bash
  cd project1-2
  python project1-2.py
  ```

### Proje 1.2d: Regresyon Analizi

**Klasör:** `project1-2d/`  
**Dosya:** `project1-2d.py`

- **Veri Seti:** Sentetik veri seti (otomatik oluşturulur, `veri_setleri/reklam_satis_veri_seti.csv`'ye kaydedilir)
- **Yöntemler:** 
  - Linear Regression
  - Ridge Regression
  - Lasso Regression
  - Random Forest Regressor
  - SVR (Support Vector Regression)
- **Metrikler:** MSE, RMSE, MAE, R²
- **Sonuç:** Lasso Regression en iyi performans (R² = 0.8879)
- **Çalıştırma:**
  ```bash
  cd project1-2d
  python project1-2d.py
  ```

### Proje 1.3: Derin Öğrenme - Görüntü Sınıflandırma

**Klasör:** `3-derinöğrenme/`  
**Dosya:** `project1-3.py`

- **Framework:** PyTorch
- **Veri Seti:** `proje_veri_seti/` (Bitki dönemleri görüntüleri)
  - Filizlenme Dönemi (35 görüntü)
  - Olgunlaşma Dönemi (35 görüntü)
  - Kış Uykusu Dönemi (35 görüntü)
- **Modeller:**
  1. **Özel CNN** (Convolutional Neural Network)
  2. **VGG16 Transfer Learning**
- **Epoch:** 5
- **Sonuç:** Her iki model de %100 test doğruluğu elde etti
- **Çalıştırma:**
  ```bash
  cd 3-derinöğrenme
  conda activate lesson
  python project1-3.py
  ```

## 📦 Gereksinimler

### Temel Kütüphaneler
```bash
pip install pandas numpy scikit-learn matplotlib seaborn
```

### Derin Öğrenme (Proje 1.3)
```bash
pip install torch torchvision pillow
# veya
conda install pytorch torchvision -c pytorch
```

### Word Dokümantasyon (Proje 1.1)
```bash
pip install python-docx
```

## 📈 Sonuçlar ve Raporlar

- **Kümeleme Analizi:** `raporlar/analiz_sonucu.txt`
- **Regresyon Analizi:** `raporlar/regresyon_analizi.txt`
- **Derin Öğrenme Analizi:** `3-derinöğrenme/DERIN_OGRENME_ANALIZ_RAPORU.txt`
- **Grafikler:**
  - `3-derinöğrenme/egitim_gecmisi.png` - Eğitim geçmişi grafikleri
  - `3-derinöğrenme/hata_matrisi.png` - Hata matrisi grafikleri

## 📝 Veri Setleri

### Acoustic Features.csv
- **Açıklama:** Müzik duygu sınıflandırma veri seti
- **Konum:** `veri_setleri/Acoustic Features.csv`
- **Örnek Sayısı:** 400
- **Öznitelik Sayısı:** 50
- **Sınıflar:** angry, happy, relax, sad

### reklam_satis_veri_seti.csv
- **Açıklama:** Reklam harcaması ve satış tahmini (sentetik)
- **Konum:** `veri_setleri/reklam_satis_veri_seti.csv`
- **Örnek Sayısı:** 200
- **Özellikler:** Reklam_Butcesi, Satis_Adedi
- **Gerçek İlişki:** y = 3x + 50 + gürültü(σ=25)
- **Not:** `project1-2d.py` çalıştırıldığında otomatik oluşturulur

## 🚀 Hızlı Başlangıç

1. **Repository'yi klonlayın veya indirin**

2. **Gereksinimleri yükleyin:**
   ```bash
   pip install pandas numpy scikit-learn matplotlib seaborn torch torchvision pillow python-docx
   ```

3. **Projeleri çalıştırın:**
   ```bash
   # Sınıflandırma
   cd project1-1 && python project1-1.py
   
   # Kümeleme
   cd ../project1-2 && python project1-2.py
   
   # Regresyon
   cd ../project1-2d && python project1-2d.py
   
   # Derin Öğrenme
   cd ../3-derinöğrenme && python project1-3.py
   ```

## 📌 Notlar

- Tüm projeler Python 3.x ile uyumludur
- Derin öğrenme projesi PyTorch kullanmaktadır
- Veri setleri `veri_setleri/` klasöründe bulunmaktadır
- Kod dosyaları kendi klasörlerinde bulunmaktadır
- Raporlar `raporlar/` klasöründe toplanmıştır

## 📄 Lisans

Eğitim amaçlı kullanım için ücretsizdir.
