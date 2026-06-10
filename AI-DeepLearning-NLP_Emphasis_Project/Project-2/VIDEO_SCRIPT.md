# Proje Tanıtım Videosu Metni
## Türkçe Metinlerde Pragmatik Vurgu Tespiti

**Hedef süre:** 6-8 dakika  
**Sunan:** Burak Yörük  
**Ders:** AI517 - Doğal Dil İşleme  
**Baz klasör:** `NLP_Emphasis_Project/Project-2`

---

## Video Akışı

| Bölüm | Süre | Amaç |
| --- | ---: | --- |
| 1. Açılış ve problem | 45 sn | Problemi ve motivasyonu anlatmak |
| 2. Veri ve yöntem | 90 sn | Notebook üzerinden veri hattını ve model tasarımını özetlemek |
| 3. Kod yapısı ve işletim | 90 sn | Notebook ve çekirdek dosyalar ile gerçek demo göstermek |
| 4. Sonuçlar | 2 dk | Final metrikleri ve sınırlılıkları sunmak |
| 5. Teslim dosyaları | 60 sn | Zip içeriğini ve son artefact'ları göstermek |
| 6. Kapanış | 30 sn | Katkı ve sonraki adım |

---

## 1. Açılış ve Problem

> "Merhaba, ben Burak Yörük. Bu videoda AI517 Doğal Dil İşleme dersi için hazırladığım `Türkçe Metinlerde Pragmatik Vurgu Tespiti` projesinin nihai teslim özetini sunuyorum."

> "Bu projenin problemi şu: Türkçede vurgu yalnız sesle değil, kelime sırası ve bağlamla da ifade ediliyor. Örneğin `Ali eve geldi` ve `Eve Ali geldi` cümlelerinde aynı sözcükler olsa da öne çıkan bilgi değişiyor."

> "Yazılı metinde ses tonu olmadığı için, bu vurguyu otomatik belirlemek özellikle metinden konuşma, diyalog sistemleri ve niyet analizi açısından önemli bir NLP problemi haline geliyor."

---

## 2. Veri ve Yöntem

### 2.1 Veri Hattı

> "Projede önce sentetik vurgu verisini işledim. Ham havuz 6 bin 253 örnekten oluşuyor. Filtreleme sonrası 5 bin 209 örnek train, validation ve test için kullanıldı."

Ekranda göster:
- `Turkish_Stress_Detection_v2_Colab.ipynb`
- notebook içindeki veri bölünmesi hücresi
- `data_loader.py`
- `data/processed/train.json`
- `data/processed/val.json`
- `data/processed/test.json`
- `data/processed/ood_test.json`

> "Ek olarak iki kamusal Türkçe veri kaynağından 1000 örneklik bir OOD, yani dağılım dışı test kümesi oluşturdum. Bu küme modelin sentetik dağılım dışındaki dayanıklılığını görmek için kullanıldı."

### 2.2 Etiketleme ve Mimari

> "Etiketleme BIO şeması ile yapılıyor: `B-EMPHASIS`, `I-EMPHASIS` ve `O`."

> "Nihai model üç ana bileşenden oluşuyor: BERTurk encoder, BIO geçişlerini denetleyen CRF decoder ve `[CLS]` temsili üzerinde çalışan supervised contrastive learning dalı."

Ekranda göster:
- `outputs/results/final_sections_3_8/section3_topology.png`

> "Buradaki amaç, yalnız toplam başarıyı artırmak değil; özellikle az görülen çok kelimeli vurgu örüntülerini daha iyi ayırt etmek."

---

## 3. Kod Yapısı ve İşletim

> "Final çalışma alanı `Project-2` klasörü. Ekran kaydında ana eksen olarak güncel demo notebook'unu açıyorum; böylece hem proje işletimini hem de hazır çıktıları tek akışta gösterebiliyorum."

Ekranda göster:

```text
Project-2/
├── config.py
├── data_loader.py
├── baseline_train.py
├── train_v2.py
├── evaluation.py
├── compare_models.py
├── models/bert_crf.py
├── paper.tex
├── paper.pdf
└── submission_stress_detection_v2.zip
```

### 3.1 Notebook Tabanlı Demo

> "İlk olarak notebook içindeki teslim dosyaları, veri bölünmesi, hazır tahmin örnekleri ve model karşılaştırma hücrelerini çalıştırıyorum. Bu bölüm projenin işletimi kısmını temsil ediyor."

Notebook'ta göster:
- teslim dosyaları özeti
- split sayıları
- sample predictions
- model comparison tablosu
- confusion matrix görselleri

> "Bu notebook ağır eğitimi tekrar etmiyor; mevcut sonuç artefact'larını kullanarak final sistemin nasıl çalıştığını ve ne ürettiğini hızlıca gösteriyor."

### 3.2 Baseline

> "İlk referans model `baseline_train.py` içindeki baseline çapraz entropi hattı. Bu model BERTurk üzerine standart token classification head kullanıyor."

### 3.3 Nihai Model

> "Asıl geliştirilmiş model `models/bert_crf.py` ve `train_v2.py` içinde yer alıyor."

Ekranda göster:
- notebook içindeki kod snippet hücresi
- `models/bert_crf.py`

Anlat:
- `AutoModel` ile BERTurk encoder
- `Linear` emission head
- CRF geçiş başlatma kuralları
- `[CLS] -> projection head -> contrastive loss`

> "CRF katmanı BIO dizisinin yapısal tutarlılığını korurken, contrastive dal cümle temsilinde tek kelimelik ve çok kelimelik vurgu örüntülerini ayrıştırmaya çalışıyor."

---

## 4. Sonuçlar

### 4.1 Ana Test Sonuçları

> "Şimdi final sonuçlara bakalım. Burada önemli nokta şu: eski abartılı doğruluk söylemi kaldırıldı. Nihai makale ve video doğrudan `outputs/results` altındaki gerçek metriklere dayanıyor."

Ekranda göster:
- `outputs/results/comparisons/model_comparison.md`
- veya `outputs/results/comparisons/model_comparison.png`

Söylenecek sayılar:

| Model						 | Split | Weighted F1 | Macro F1 | I-EMPHASIS F1 | I-EMPHASIS Recall |
| ---							 | --- | ---: | ---: | ---: | ---: |
| Baseline CE 			| Test | 0.8820 | 0.6607 | 0.4375 | 0.3333 |
| BERT+CRF+SCL | Test | 0.8842 | 0.7026 | 0.5556 | 0.4762 |

> "Weighted F1 artışı sınırlı, ama araştırma açısından daha kritik olan `I-EMPHASIS` sınıfında belirgin iyileşme var. Yani model özellikle zor ve seyrek vurgu örüntülerinde daha iyi davranıyor."

### 4.2 OOD Sonuçları

> "OOD testinde ise weighted F1 yaklaşık sabit kalıyor, fakat `I-EMPHASIS` performansı sıfıra düşüyor."

| Model | Split | Weighted F1 | Macro F1 | I-EMPHASIS F1 |
| --- | --- | ---: | ---: | ---: |
| Baseline CE | OOD | 0.8500 | 0.3181 | 0.0000 |
| BERT+CRF+SCL | OOD | 0.8487 | 0.3196 | 0.0000 |

> "Bu da bize şunu söylüyor: model sentetik dağılım içinde umut verici, ama gerçek dünya benzeri dağılımlarda daha fazla manuel denetimli veriye ihtiyaç var."

### 4.3 Kısa Sonuç Cümlesi

> "Yani bu proje tam olarak iki şeyi gösteriyor: birincisi CRF+SCL hattı azınlık sınıfında faydalı; ikincisi OOD genelleme hâlâ açık problem."

---

## 5. Teslim Dosyaları

> "Final teslim paketini `submission_stress_detection_v2.zip` dosyası temsil ediyor."

Ekranda göster:
- `submission_stress_detection_v2.zip`
- zip içeriği

Vurgulanacak dosyalar:
- `paper.tex`
- `paper.pdf`
- `Proje-final-raporu.docx`
- `presentation_marp/final-presentation-marp.pdf`
- `Presentation_II/presentation-II.pdf`
- `config.py`, `data_loader.py`, `train_v2.py`, `evaluation.py`, `compare_models.py`
- `outputs/results/*`

> "Bugünkü teslim mantığı şu: makale, rapor, sunum, kod ve sonuç artefact'ları aynı klasör hattında toplanmış durumda. Video da bu nihai paketi açıklayan ek teslim olarak hazırlanıyor."

---

## 6. Kapanış

> "Özetle, bu çalışmada Türkçe pragmatik vurgu tespiti için sentetik veri üretimi, BERTurk, CRF ve supervised contrastive learning bir araya getirildi. Final sonuçlar, toplam skordan çok azınlık sınıf metriklerinin takip edilmesi gerektiğini gösterdi."

> "Bir sonraki doğal adım, OOD etiketlerinin manuel denetimi ve daha gerçek veriyle genellemenin güçlendirilmesi olacaktır."

> "İzlediğiniz için teşekkür ederim."

---

## Ekran Paylaşımı Planı

1. `Turkish_Stress_Detection_v2_Colab.ipynb`
2. notebook içindeki teslim dosyaları özeti
3. notebook içindeki veri bölünmesi ve sample predictions hücreleri
4. notebook içindeki model comparison tablosu
5. notebook içindeki confusion matrix ve topology görselleri
6. notebook içindeki `models/bert_crf.py` snippet'i
7. `paper.pdf`
8. `submission_stress_detection_v2.zip`

---

## Video Çekim Notları

- Açılışı tek kişi yap: ekip anlatısı yerine final sahipliği net olsun.
- Abartılı doğruluk söylemi kullanma; gerçek metrikleri kullan.
- Demo için notebook'u ana pencere yap; makale PDF'sini ikinci pencerede açık tut.
- Hazır çıktıları göstererek ilerle; ağır eğitim başlatma.
- Kısa bir "işletim" hissi için notebook hücrelerini canlı çalıştır.
- Eğer süre daralırsa, `Kod Yapısı` bölümünü 60 saniyeye indir ve `Sonuçlar` bölümünü koru.

---

## Zorunlu Dosyalar

- `paper.pdf`
- `submission_stress_detection_v2.zip`
- `outputs/results/comparisons/model_comparison.md`
- `outputs/results/test/confusion_matrix.png`
- `outputs/results/final_sections_3_8/section3_topology.png`
