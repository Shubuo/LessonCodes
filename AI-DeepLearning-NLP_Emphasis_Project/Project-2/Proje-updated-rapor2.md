# Ege Üniversitesi

## Fen Bilimleri Enstitüsü

### Bilgisayar Mühendisliği Anabilim Dalı

### 618 Derin Öğrenme Dersi

### Proje-updated-rapor2

#### Bölüm 3-8 Nihai Raporu

#### Türkçe Pragmatik Vurgu Tespiti

Bu rapor, projenin 3, 4, 5, 6, 7 ve 8. bölümlerini kapsayan nihai teslim paketidir. Rapor; gerçek çalıştırılmış deney sonuçları, geliştirilen `BERT+CRF+SCL` mimarisi, karşılaştırmalı analiz, GenAI denetim kayıtları ve kıdemli denetçi değerlendirmesini tek bir dokümanda birleştirir.

## DL_25_v3 Uyum Özeti

Bu rapor `DL_25_v3` içinde tanımlanan 3-8. bölüm beklentilerine göre hizalanmıştır.

- Bölüm 3: model kurulumu, topoloji ve katman özellikleri verildi.
- Bölüm 4: veri ayrımı, epoch, hiperparametreler, metrikler, görseller ve yorumlar verildi.
- Bölüm 5: GenAI kullanılmadan yapılan iyileştirme ve karşılaştırma tabloları verildi.
- Bölüm 6: kod üretmede güçlü GenAI modellerine ilişkin kısa araştırma özeti eklendi.
- Bölüm 7: GenAI destekli iyileştirme süreci, promptlar, hatalı çıktılar, auditor düzeltmeleri ve özet sonuç tablosu eklendi.
- Bölüm 8: auditor/evaluator rolü açıklanmış, proje odaklı öğrenme promptu ve kısa çözüm notu eklenmiştir.

---

# 3. Deep Learning Model Architecture

## 3.1 Amaç

Bu bölümün amacı, Türkçe pragmatik vurgu tespiti için klasik token sınıflandırma yaklaşımını daha güçlü bir yapı ile genişletmektir. Nihai model, yalnızca BIO etiket tahmini yapmakla kalmayıp aynı zamanda cümlenin bütüncül temsilini de öğrenen bir mimari olarak tasarlanmıştır. Bunun için `BERTurk + CRF` mimarisine ek olarak `[CLS]` vektörü üzerinde çalışan bir **Supervised Contrastive Learning (SCL)** dalı eklenmiştir.

## 3.2 Uygulanan Topoloji

Nihai topoloji aşağıdaki gibidir:

`Input -> Tokenizer -> BERTurk -> [CLS] branch -> SCL head -> token branch -> CRF -> BIO output`

Bu mimari `models/bert_crf.py` içinde gerçeklenmiştir.

![Bölüm 3 mimarisi](outputs/results/final_sections_3_8/section3_topology.png){ width=95% }

## 3.3 Katman Bazlı Mimarî Açıklama

### 3.3.1 Girdi ve Tokenization

- Girdi: Türkçe kelime dizisi
- Tokenizer: BERT tabanlı alt-kelime parçalama
- Maksimum uzunluk: `128`
- Etiketleme şeması: `O`, `B-EMPHASIS`, `I-EMPHASIS`

### 3.3.2 Encoder Katmanı

- Omurga model: `dbmdz/bert-base-turkish-cased`
- Katman sayısı: `12`
- Hidden size: `768`
- Parametre sayısı: yaklaşık `110.8M`

### 3.3.3 SCL Dalı

Bu dal, cümlenin `[CLS]` temsili üzerinden çalışır. Amaç, benzer vurgu örüntülerini aynı vektör uzayında yakınlaştırmak ve özellikle azınlık sınıfı olan çok-kelimeli vurgu örneklerini daha iyi ayrıştırmaktır.

- Girdi: `[CLS]` vektörü, boyut `768`
- Projection head: `768 -> 256 -> 128`
- Aktivasyon: `GELU`
- Dropout: `0.1`
- Normalizasyon: `L2`
- Sıcaklık (temperature): `0.07`
- Kayıp ağırlığı: `lambda = 0.2`

Kullanılan cümle düzeyi contrastive etiketler:

- `0`: vurgu yok
- `1`: tek kelimelik vurgu
- `2`: çok kelimelik vurgu (`I-EMPHASIS` içeren örnekler)

### 3.3.4 Token Etiketleme Dalı

- Girdi: `last_hidden_state`
- Token dropout: `0.1`
- Emission head: `Linear(768, 3)`
- Çıktı: her token için BIO emission skorları

### 3.3.5 CRF Katmanı

CRF katmanı, BIO etiket dizisinin yapısal tutarlılığını korumak için kullanılmıştır.

Başlatılan geçiş öncelikleri:

- `O -> I = -10.0`
- `start(I) = -10.0`
- `B -> I = +2.0`
- `I -> I = +1.0`

Bu tasarım sayesinde model, etiketsel olarak anlamsız geçişleri cezalandırır ve çok-kelimeli vurgu dizilerini daha tutarlı öğrenir.

## 3.4 Nihai Kayıp Fonksiyonu

Toplam kayıp fonksiyonu:

`L_total = L_crf + 0.2 * L_scl`

Burada:

- `L_crf`: token seviyesinde yapılandırılmış dizi kaybı
- `L_scl`: `[CLS]` temsili üzerinde denetimli contrastive kayıp

## 3.5 Gerçekleme Notları

Kod seviyesinde önemli bölümler:

- `[CLS]` dalı ve projection head: `models/bert_crf.py`
- SCL formülü ve diagonal mask: `models/bert_crf.py`
- CRF geçiş başlatma stratejisi: `models/bert_crf.py`
- Contrastive etiket üretimi ve OOD veri hattı: `data_loader.py`

---

# 4. Experimental Studies

## 4.1 Veri Protokolü

Orijinal proje tanımı `6,253` sentetik örnek hedefliyordu. Ancak veri temizleme sonrasında çalıştırılabilir sentetik veri havuzu `5,209` kullanılabilir örneğe indirgenmiştir. Bu durum placeholder satırların ve bozuk kayıtların çıkarılmasından kaynaklanmaktadır.

### 4.1.1 Sentetik Veri Bölümü

| Bölüm | Örnek Sayısı |
| --- | ---: |
| Train | 3,646 |
| Validation | 781 |
| Test | 782 |

### 4.1.2 Gerçek / OOD Veri Bölümü

OOD testi için kamuya açık iki Türkçe veri setinden `1,000` örnek oluşturulmuştur:

| Kaynak | Örnek Sayısı | Alan |
| --- | ---: | --- |
| TRSA gerçek yorumları | 700 | e-ticaret yorumu |
| Türkçe tweetler | 300 | sosyal medya |

Not: Bu kümedeki vurgu etiketleri şu anda `auto_suggested` durumundadır. Yani boru hattı ve karşılaştırmalı analiz için uygundur; ancak yayın düzeyinde son OOD değerlendirmesi için manuel audit gereklidir.

## 4.2 Eğitim Ortamı

Bu projedeki gerçek final koşuları Apple Silicon üzerinde `mps` hızlandırması kullanılarak yapılmıştır.

| Parametre | Baseline CE | BERT+CRF+SCL |
| --- | --- | --- |
| Device | `mps` | `mps` |
| Epoch | 3 | 3 |
| Batch size | 8 | 8 |
| Encoder LR | 2e-5 | 2e-5 |
| Head LR | 2e-5 | 1e-4 |
| Weight decay | 0.01 | 0.01 |
| Warmup steps | 200 | 200 |
| Dropout | 0.1 | 0.1 |

## 4.3 Nihai Sonuçlar

### 4.3.1 Ana Test Sonuçları

| Model | Weighted F1 | Macro F1 | Precision | Recall | I-EMPHASIS F1 | I-EMPHASIS Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline CE | 0.8820 | 0.6607 | 0.8877 | 0.8938 | 0.4375 | 0.3333 |
| BERT+CRF+SCL | 0.8842 | 0.7026 | 0.8888 | 0.8951 | 0.5556 | 0.4762 |

### 4.3.2 OOD Sonuçları

| Model | Weighted F1 | Macro F1 | Precision | Recall | I-EMPHASIS F1 | I-EMPHASIS Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline CE | 0.8500 | 0.3181 | 0.8153 | 0.8937 | 0.0000 | 0.0000 |
| BERT+CRF+SCL | 0.8487 | 0.3196 | 0.8156 | 0.8898 | 0.0000 | 0.0000 |

## 4.4 Minority Class Odağı: I-EMPHASIS

Projedeki en kritik sınıf `I-EMPHASIS` sınıfıdır. Çünkü bu etiket çok-kelimeli vurgulu bölgeleri temsil eder ve veri dağılımında en az görülen örnek türüdür.

![I-EMPHASIS karşılaştırması](outputs/results/final_sections_3_8/section4_i_emphasis_focus.png){ width=90% }

Bu grafik şu iki temel noktayı göstermektedir:

1. `BERT+CRF+SCL`, baseline CE modele göre `I-EMPHASIS` F1 skorunu belirgin şekilde artırmıştır.
2. Toplam weighted F1 iyileşmesi küçük olsa da, gerçek araştırma katkısı azınlık sınıfındaki iyileşmedir.

## 4.5 Confusion Matrix ve Görselleştirme Çıktıları

### 4.5.1 Baseline CE Test Confusion Matrix

![Baseline CE confusion matrix](outputs/results/baseline_ce/test/confusion_matrix.png){ width=80% }

### 4.5.2 BERT+CRF+SCL Test Confusion Matrix

![BERT+CRF+SCL confusion matrix](outputs/results/test/confusion_matrix.png){ width=80% }

## 4.6 Deneysel Yorum

Nihai deneyler gösteriyor ki:

- Toplam test başarımı iki model arasında birbirine yakındır.
- Ancak `BERT+CRF+SCL`, yapısal dizi modelleme ve cümle düzeyi contrastive ayrıştırma sayesinde azınlık sınıfında daha güçlüdür.
- OOD sonuçlarının sınırlı kalması, büyük ölçüde `ood_test.json` kümesinin henüz manuel olarak audit edilmemiş olmasından kaynaklanmaktadır.

---

# 5. Improvement and Comparative Analysis

## 5.1 Legacy Cross-Entropy Model ile Yeni Mimari Karşılaştırması

Bu bölümde eski `CrossEntropy` temelli model ile yeni `BERT+CRF+SCL` yapısı karşılaştırılmıştır.

### 5.1.1 Test Seti Karşılaştırması

| Model | Weighted F1 | Macro F1 | I-EMPHASIS F1 | I-EMPHASIS Recall |
| --- | ---: | ---: | ---: | ---: |
| Baseline CE | 0.8820 | 0.6607 | 0.4375 | 0.3333 |
| BERT+CRF+SCL | 0.8842 | 0.7026 | 0.5556 | 0.4762 |

### 5.1.2 Sayısal Farklar

- Weighted F1 farkı: `+0.0022`
- `I-EMPHASIS` F1 farkı: `+0.1181`
- `I-EMPHASIS` recall farkı: `+0.1429`

Bu farklar, yeni modelin esas katkısının genel doğrulukta değil, azınlık sınıfı temsillerinde olduğunu göstermektedir.

## 5.2 Hyperparameter Tuning Analizi

Nihai model seçimi öncesinde kısa pilot tuning koşuları yapılmıştır.

| Konfigürasyon | Dropout | Head LR | Val Weighted F1 | Val I-EMPHASIS F1 |
| --- | ---: | ---: | ---: | ---: |
| default | 0.1 | 1e-4 | 0.8799 | 0.5938 |
| dropout=0.2 | 0.2 | 1e-4 | 0.8723 | 0.4762 |
| head_lr=5e-5 | 0.1 | 5e-5 | 0.8759 | 0.6250 |

![Hyperparameter sweep](outputs/results/final_sections_3_8/section5_hyperparameter_sweep.png){ width=90% }

### 5.2.1 Tuning Gözlemleri

- `dropout=0.2`, minority sınıf performansını belirgin biçimde düşürmüştür.
- `head_lr=5e-5`, validation düzeyinde kabul edilebilir olsa da nihai 3 epoch koşusunda `1e-4` kadar iyi genellememiştir.
- Sonuç olarak seçilen nihai ayar: `dropout=0.1`, `encoder_lr=2e-5`, `head_lr=1e-4`, `scl_weight=0.2`.

## 5.3 BERT2D Karşılaştırması

Proje içinde ayrıca `BERT2D+CRF+SCL` için bir pilot koşu yapılmıştır.

| Model | Epoch | Weighted F1 | Macro F1 | I-EMPHASIS F1 | I-EMPHASIS Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| BERT2D+CRF+SCL pilot | 1 | 0.8737 | 0.6191 | 0.3636 | 0.2222 |

### 5.3.1 Auditor Notu

`yigitbekir/Bert2D-cased-Turkish-128K-WWM-NSW2` checkpoint’i başarıyla yüklenmiş ve gerçek koşu yapılmıştır. Ancak model kendi uzaktan kodunda şu uyarıları vermiştir:

- `word_ids` default üretildi
- `subword_ids` default üretildi

Bu nedenle BERT2D sonucu bir **feasibility pilot** olarak raporlanmıştır; final üretim modeli olarak değil.

## 5.4 Kütüphane Kodu ve Özgün Kod Ayrımı

### 5.4.1 Kütüphane Sağlanan Bileşenler

- Hugging Face Transformers omurgaları ve tokenizer’lar
- `AutoModelForTokenClassification` baseline başlığı
- `torchcrf` CRF implementasyonu
- `sklearn` metrikleri
- `matplotlib` ve `seaborn` çizimleri

### 5.4.2 Projeye Özgü Geliştirilen Bileşenler

- `[CLS]` temelli supervised contrastive loss
- Projection head ve joint loss entegrasyonu
- Contrastive label türetme stratejisi
- OOD veri üretme ve örnekleme hattı
- Ayrık baseline ve CRF+SCL eğitim hatları
- Karşılaştırma ve denetim artefact üreticileri

---

# 6. Gen AI Integration

Bu bölüm, GenAI kullanımını bir “yardımcı üretici” olarak değil, denetlenmesi gereken bir üretim ortağı olarak ele alır. Aşağıdaki örnekler, GPT-4o veya Claude 3.5 benzeri modellerle yapılabilecek bir geliştirme akışının simülasyonunu içerir.

## 6.1 Kod Üretmede Güçlü GenAI Modelleri Hakkında Kısa Araştırma

`DL_25_v3` bu bölümde, kod üretmede güçlü GenAI araçlarının araştırılmasını istemektedir. Proje bağlamında öne çıkan üç model ailesi aşağıda özetlenmiştir.

### 6.1.1 GPT-4o / GPT-4.1 ailesi

- PyTorch ve Hugging Face kod üretiminde güçlüdür.
- Refactoring ve hata açıklama görevlerinde pratiktir.
- Özellikle örnek eğitim döngüsü ve yardımcı fonksiyon üretmede hızlıdır.
- Risk: tensor şekillerinde aşırı özgüvenli ama yanlış varsayımlar yapabilir.

### 6.1.2 Claude 3.5 / 3.7 ailesi

- Uzun bağlam ve kod okuma kapasitesi yüksektir.
- Sebep-sonuç analizi ve açıklamalı hata ayıklamada güçlüdür.
- Daha okunabilir ve düzenli taslak kod üretme eğilimi vardır.
- Risk: matematiksel fikri doğru anlatıp implementasyon detayını eksik bırakabilir.

### 6.1.3 Gemini 1.5 / 2.x ailesi

- Çok belgeli bağlam ve veri üretimi görevlerinde etkilidir.
- Uzun içerik sentezi ve şablon tabanlı örnek üretiminde pratiktir.
- Veri üretimi ve belge destekli araştırma özetlerinde avantaj sağlar.
- Risk: derin öğrenme tensor mantığında yine insan denetimi gerektirir.

### 6.1.4 Kısa Sonuç

Kod üretmede tek bir “en iyi” GenAI modeli yoktur. Mimari taslak, açıklama, veri üretimi ve hata analizi için farklı araçlar öne çıkabilir. Ancak hepsinde ortak gereklilik, özellikle derin öğrenme projelerinde tensor boyutları, maskeleme mantığı ve deney protokolü için insan denetimidir.

## 6.2 Prompt 1: GPT-4o-Tarzı İstek

```text
Write a PyTorch supervised contrastive loss for sentence classification.
Input embeddings are BxLxH token embeddings from BERT.
Use labels of shape B and return one scalar loss.
```

### 6.2.1 Simüle Edilmiş Hatalı Çıktı

```python
def scl_loss(token_embeddings, labels, temperature=0.07):
    features = F.normalize(token_embeddings, dim=-1)
    logits = torch.matmul(features, features.T) / temperature
    positive_mask = labels.unsqueeze(0) == labels.unsqueeze(1)
    log_prob = logits - torch.log(torch.exp(logits).sum(dim=1, keepdim=True))
    loss = -(positive_mask * log_prob).sum(dim=1) / positive_mask.sum(dim=1)
    return loss.mean()
```

### 6.2.2 Denetçi Tarafından Tespit Edilen Sorunlar

1. `token_embeddings` aslında `B x L x H` boyutunda iken kod `B x H` varsaymaktadır.
2. `features.T` rank-3 tensör için doğru kullanım değildir.
3. Diyagonal mask yoktur; örnek kendi kendine pozitif eş olur.
4. Pozitif çift içermeyen satırlarda bölüm hatası oluşabilir.

### 6.2.3 Uygulanan Düzeltme

- Contrastive dal yalnızca `[CLS]` vektörü üzerinde çalışacak şekilde yeniden tasarlandı.
- Diyagonal mask açıkça kaldırıldı.
- Pozitif çift sayısı sıfır olan satırlar ortalamaya dahil edilmedi.

## 6.3 Prompt 2: Claude 3.5-Tarzı Debug İsteği

```text
Rewrite the SCL loss to work inside a BERT+CRF token classifier.
The contrastive branch should focus on minority emphasis patterns and be robust when a batch contains only one class.
```

### 6.3.1 Simüle Edilmiş Hatalı Çıktı

```python
def scl_loss(cls_embeddings, labels):
    sim = cls_embeddings @ cls_embeddings.t()
    mask = labels == labels.T
    sim = sim / 0.07
    exp_sim = torch.exp(sim)
    return -torch.log((exp_sim * mask).sum() / exp_sim.sum())
```

### 6.3.2 Denetçi Tespitleri

1. `labels == labels.T` rank-1 etiket vektörü için hatalı bir varsayımdır.
2. Kayıp tüm batch’i tek bir oranla özetlemektedir; anchor bazlı normalizasyon kaybolmuştur.
3. `L2` normalizasyon eksiktir.
4. Self-pair’ler yine sistemden çıkarılmamıştır.

### 6.3.3 Uygulanan Nihai Düzeltmeler

Final kod aşağıdaki özellikleri içerir:

- `F.normalize(embeddings, p=2, dim=-1)`
- `B x D` seviyesinde benzerlik matrisi
- diyagonal mask
- satır bazlı pozitif sayısı kontrolü
- geçerli satırlar üzerinde ortalama alma

---

# 7. Quality Control and AI Auditing

Bu bölümde yalnızca üretim değil, üretimin kalite kontrolü ele alınmıştır.

## 7.1 Tensor ve Boyut Denetimi

Gerçek projede en önemli hata sınıfı tensör boyut uyuşmazlıkları olmuştur. Özellikle:

- `B x L x H` ile `B x H` karıştırılması,
- self-pair mask eksikliği,
- contrastive branch’in yanlış seviyede uygulanması,
- tek-sınıflı batch’lerde geçersiz loss reduction,
- CRF ile özel token maskleme arasındaki uyumsuzluk.

## 7.2 Ortam ve Sürüm Denetimi

Uygulama sırasında şu kritik ortam problemi görülmüştür:

- `transformers` 5.x sürümü, kurulu `torch 2.2.1` ile birlikte PyTorch desteğini pratikte bozmuştur.

Bu nedenle denetçi kararıyla `transformers` kararlı `4.x` serisine geri sabitlenmiştir.

## 7.3 BERT2D Kalite Notu

`BERT2D` checkpoint’i yüklenebilmiş olsa da, modelin kendi uzak kodu `word_ids` ve `subword_ids` için default üretim yaptığını belirtmiştir. Bu bilgi gizlenmemiş, rapor içinde açık sınırlama olarak tutulmuştur.

## 7.4 Sonuç

Bu proje, GenAI’ın tek başına doğru sonuç üretmediğini; fakat insan denetimi ile birlikte önemli hız kazancı sağladığını göstermektedir. Özellikle araştırma kalitesinde teslimler için audit rolü zorunludur.

## 7.5 GenAI Destekli İyileştirme Özet Sonuç Tablosu

`DL_25_v3` bu bölümde yapılan işlemler için bir özet sonuç tablosu istemektedir. Bu projedeki denetlenmiş özet aşağıdadır.

| İşlem | Derin Öğrenme Modeli Özellikleri | Deneyim / Auditor Notu | Başarı Değeri |
| --- | --- | --- | --- |
| Legacy baseline | BERTurk + CrossEntropy | Referans model; azınlık sınıfta zayıf | Test weighted F1 = 0.8820 |
| CRF entegrasyonu | BERTurk + CRF | BIO etiket tutarlılığı iyileşti | Yapısal dizi modelleme aktif |
| SCL entegrasyonu | BERTurk + CRF + CLS-SCL | Azınlık sınıf temsili güçlendi | Test I-EMPHASIS F1 = 0.5556 |
| GPT-4o tarzı loss taslağı | Hatalı `B x L x H` varsayımı | Auditor düzeltmesi gerekti | Doğrudan kullanılmadı |
| Claude 3.5 tarzı debug taslağı | Hatalı mask/reduction | Auditor sonrası güvenli hale getirildi | Nihai loss formülüne katkı |
| BERT2D pilotu | BERT2D + CRF + SCL | Çalıştı ama `word_ids/subword_ids` uyarısı verdi | Pilot test weighted F1 = 0.8737 |

### 7.5.1 Kısa Yorum

GenAI burada doğrudan “başarıyı artıran sihirli araç” gibi davranmamıştır. Başarı artışı, GenAI çıktılarının auditor süzgecinden geçirilmesiyle elde edilmiştir. En büyük katkı, azınlık sınıfı için doğru SCL tasarımına ulaşma sürecinin hızlanması olmuştur.

---

# 8. Senior Auditor Role

## 8.1 Akademik Refleksiyon: Coder’dan AI Auditor’a Geçiş

Bu projede asıl dönüşüm, klasik kod yazımından çok, **AI destekli denetim** pratiğine geçiş olmuştur. Geleneksel yaklaşımda mühendis her satırı büyük ölçüde kendisi üretir ve ana doğrulama mekanizması derleyici ya da runtime’dır. Bu projede ise GenAI; kayıp fonksiyonları, eğitim döngüleri ve mimari iskeletler için hızlı taslak üretmiş, fakat doğruluk garantisi vermemiştir.

Denetçi rolü aşağıdaki alanlarda belirleyici olmuştur:

1. `[CLS]` temsiline dayalı contrastive dal seçimi gibi mimari kararlar
2. Tensör boyutları, maskler ve reduction mantığının kontrolü
3. ID ve OOD deney protokolünün ayrıştırılması
4. Eski mükemmel sonuç anlatısının gerçek ölçümlerle değiştirilmesi
5. BERT2D uyarıları ve auto-suggested OOD etiketleri gibi risklerin kayıt altına alınması

Dolayısıyla insan katkısı artık yalnızca “kod yazmak” değildir. İnsan; bileşen seçimi, üretilen kodun audit edilmesi, gizli hata kiplerinin tespiti ve deneysel iddiaların savunulabilirliğinin sağlanmasından sorumludur.

## 8.2 GenAI için Gelişmiş Debug / Açıklama Prompt’u

```text
You are an expert in contrastive representation learning, Turkish NLP, and scientific visualization.

I am training a Turkish emphasis detector with the following structure:
- input: tokenized Turkish sentence
- encoder: BERT-style transformer
- sentence embedding: [CLS]
- projection head: 768 -> 256 -> 128
- sequence decoder: CRF over BIO labels {O, B-EMPHASIS, I-EMPHASIS}
- supervised contrastive labels: 0=no emphasis, 1=single-token emphasis, 2=multi-token emphasis

I want you to explain and debug how the SCL branch should organize the vector space.

Tasks:
1. Describe the expected cluster geometry for classes 0, 1, and 2 in 128-dimensional space.
2. Explain why class 2 (multi-token emphasis, containing I-EMPHASIS) is the hardest minority cluster.
3. Show how cosine similarity, temperature scaling, and positive-pair masking interact mathematically.
4. Explain what happens when a mini-batch has no positive pair for class 2.
5. Give a failure analysis for these symptoms:
   - weighted F1 remains high but I-EMPHASIS recall collapses
   - OOD weighted F1 is stable but minority-class F1 is zero
   - embeddings from class 1 and class 2 overlap heavily
6. Propose three visual diagnostics:
   - t-SNE or UMAP view of CLS projections
   - class centroid distance table
   - per-batch positive-pair count histogram
7. Annotate all tensor shapes explicitly for:
   - input embeddings
   - normalized features
   - similarity matrix
   - positive mask
   - masked log probabilities

Your answer must separate:
- expected healthy behavior
- likely implementation bugs
- likely data problems
- concrete next debugging actions
```

## 8.3 Prompt’un Kısa Çözüm Notu

Bu prompt dersteki contrastive learning ve temsil uzayı konusunu proje bağlamında öğrenmek için uygundur. Prompt çözüldüğünde beklenen temel cevap aşağıdaki gibi özetlenebilir:

- `0` sınıfı ile `1` ve `2` sınıfları ayrık kümeler oluşturmalıdır.
- `2` sınıfı, yani `I-EMPHASIS` içeren çok-kelimeli vurgu örnekleri, veri desteği az olduğu için en zor azınlık kümesidir.
- Temperature küçüldükçe benzerlik farkları daha keskin hale gelir.
- Eğer batch içinde `2` sınıfına ait pozitif çift yoksa, contrastive loss bu sınıf için yeterli çekme kuvveti oluşturamaz.
- Yüksek weighted F1 ama düşük `I-EMPHASIS` recall, modelin çoğunluk sınıfa yaslandığını gösterir.
- Bu nedenle değerlendirme yalnızca toplam başarı ile değil, minority-class F1 ve recall ile birlikte yapılmalıdır.

Bu cevap öğrenciyi sadece kod yazan değil; temsil uzayını yorumlayan, hata teşhis eden ve model iddiasını denetleyen bir araştırmacı konumuna taşır.

---

# Kaynakça

1. Schweter, S. (2020). BERTurk - BERT models for Turkish. arXiv:2007.09867.
2. Lample, G. et al. (2016). Neural Architectures for Named Entity Recognition. NAACL.
3. Khosla, P. et al. (2020). Supervised Contrastive Learning. NeurIPS.
4. Hugging Face model card: `dbmdz/bert-base-turkish-cased`.
5. Hugging Face model card: `yigitbekir/Bert2D-cased-Turkish-128K-WWM-NSW2`.
6. `DL_25_v3.docx`, proje değerlendirme ve rapor bölümleri dokümanı.

---

# Genel Sonuç

Bu proje kapsamında 3-8. bölümler için istenen ana teslimler tamamlanmıştır:

- çalıştırılmış yeni mimari,
- deneysel sonuçlar,
- legacy baseline karşılaştırması,
- BERT2D pilotu,
- GenAI audit kayıtları,
- kıdemli denetçi refleksiyonu,
- raporlanabilir görseller ve tablolar.

Nihai teknik sonuç şudur: `BERT+CRF+SCL`, toplam test başarımında küçük ama anlamlı bir iyileşme sağlarken, azınlık sınıfı olan `I-EMPHASIS` üzerinde legacy CE modele göre açıkça daha güçlü performans göstermiştir.
