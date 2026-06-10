# Ege Üniversitesi

## Fen Bilimleri Enstitüsü

### Bilgisayar Mühendisliği Anabilim Dalı

### 618 Derin Öğrenme Dersi

### Proje 1 Final Raporu

## Türkçe Dizilim Etiketleme Görevlerinde Gözetimli Karşıtlamalı Öğrenme Destekli Büyük Dil Modelleri:

## Pragmatik Vurgu Tespiti Üzerine Dağılım Dışı Sağlamlık Analizi

**Hazırlayan:** Burak YÖRÜK  
**Öğrenci No:** 91250000324  
**Dönem:** 2025-2026 Bahar Yarıyılı  
**Rapor Türü:** Birleştirilmiş Nihai Teslim Raporu

---

# Özet

Bu rapor, proje sürecindeki ön rapor ve final uygulama aşamalarını tek bir bütünleşik teslim dokümanında birleştirmektedir. Çalışmanın amacı, Türkçe yazılı metinlerde pragmatik vurgunun otomatik tespitidir. Problem, özellikle Türkçenin serbest sözcük dizilişi ve sondan eklemeli morfolojik yapısı nedeniyle klasik kural tabanlı yöntemlerle güvenilir biçimde modellenememektedir. Bu nedenle proje, büyük dil modeli tabanlı dizilim etiketleme yaklaşımını benimsemiştir.

Çalışmanın erken aşamasında literatür ve veri stratejisi açısından `BERT`, `RoBERTa`, `CRF`, `Supervised Contrastive Learning`, `BERT2D`, `ConvBERTurk` ve `SindBERT` gibi modeller incelenmiştir. Son uygulama aşamasında ise çalıştırılabilir ve denetlenebilir ana model olarak `BERTurk + CRF + CLS-temelli Supervised Contrastive Learning` yapısı geliştirilmiştir. Deneylerde temizlenmiş sentetik BIO etiketli veri ile kamuya açık gerçek/OOD Türkçe veri kaynakları birlikte kullanılmıştır. Elde edilen sonuçlar, toplam weighted F1 skorunda sınırlı fakat istikrarlı bir iyileşme olduğunu; buna karşılık azınlık sınıfı olan `I-EMPHASIS` üzerinde daha belirgin bir kazanım sağlandığını göstermektedir.

Bu rapor ayrıca `DL_25_v3` rubricindeki tüm maddeleri tek tek karşılayacak şekilde düzenlenmiştir: model araştırması, veri seti ve konu belirleme, model oluşturma, deneysel çalışmalar, GenAI kullanmadan iyileştirme ve karşılaştırma, kod üretmede GenAI araştırması, GenAI destekli iyileştirme denemeleri, auditor/evaluator rolü tartışması, kaynakça ve özdeğerlendirme tablosu. Ayrıca teslim dosyasına dahil edilen kaynak kodlar ve sonuç artefact’ları için ayrı ek listeleri eklenmiştir.

**Anahtar Kelimeler:** Türkçe NLP, pragmatik vurgu, token classification, BERTurk, CRF, supervised contrastive learning, OOD robustness, GenAI auditing.

---

# İçindekiler Notu

Bu rapor aşağıdaki ana bölümlerden oluşmaktadır:

1. Model Hakkında Araştırma  
2. Veri Seti ve Konu Belirleme  
3. Derin Öğrenme Modelinin Oluşturulması  
4. Deneysel Çalışmalar  
5. İyileştirme ve Karşılaştırma  
6. Araştırma: Kod Üretmede Gen AI  
7. Gen AI Desteği ile İyileştirme  
8. Evaluator / Auditor Rolü  
9. Özdeğerlendirme Tablosu  
10. Kaynakça  
11. Ekler: Teslime Dahil Edilen Kod ve Dosyalar

---

# 1. Model Hakkında Araştırma

Doğal dil işleme alanında bağlama duyarlı anlamsal temsillerin çıkarılmasında Transformer tabanlı çift yönlü kodlayıcılar olan `BERT` ve `RoBERTa` mimarileri temel standardı oluşturmaktadır. Bu modeller, metindeki her tokenin hem sol hem sağ bağlam ile birlikte temsil edilmesini sağlayarak klasik sıralı modellere kıyasla çok daha güçlü anlamsal gömmeler üretir. Bununla birlikte, token classification ve sequence labeling gibi görevlerde yalnızca bağımsız softmax başlığı kullanmak, Türkçe gibi karmaşık morfolojik ve sözdizimsel kısıtlara sahip dillerde etiket dizisinin tutarlılığını garanti etmez. Bu nedenle `Conditional Random Fields (CRF)` katmanı, özellikle `BIO` şemasında anlamsız geçişleri engellemek için güçlü bir tamamlayıcı katman olarak öne çıkmaktadır. `CRF`, tek tek tokenlerin olasılıklarını değil, tüm etiket dizisinin ortak olasılığını optimize eder ve Viterbi çözümlemesiyle en tutarlı etiket yolunu seçer.

Ancak pragmatik vurgu tespiti gibi çok dengesiz veri dağılımlarına sahip görevlerde, yalnızca `Cross-Entropy` ya da `CRF` optimizasyonu çoğu zaman yeterli değildir. Son yıllarda `Supervised Contrastive Learning (SCL)` teknikleri, benzer sınıfa ait örnekleri gömme uzayında birbirine yaklaştırırken farklı sınıfları ayırarak temsillerin ayrıştırıcılığını artırdığı için önemli hale gelmiştir. Türkçe özelinde `BERTurk-contrastive` gibi çalışmalar anlamsal benzerlik görevlerinde güçlü sonuçlar verirken, `BERT2D` gibi mimariler ise Türkçenin alt-kelime ve kelime düzeyi yapısını birlikte modelleyerek morfolojik zenginliği daha iyi yakalayabilmektedir. Bu proje, ön araştırmadan gelen bu literatür bilgisini, pratik ve çalıştırılabilir bir nihai sistem tasarımına dönüştürerek `BERTurk + CRF + SCL` hattını ana model olarak seçmiştir.

---

# 2. Veri Seti ve Konu Belirleme

## 2.1 Problem Tanımı

Bu çalışmanın temel problemi, Türkçe yazılı metinlerde konuşma dilinde tonlama ve odakla aktarılan pragmatik vurgunun otomatik olarak tespit edilmesidir. Sözlü iletişimde vurgu, perde, süre ve ses şiddeti gibi akustik sinyaller ile iletilirken, yazılı metin bu ipuçlarını doğrudan taşımaz. Buna ek olarak Türkçenin sözcük dizilişinde esnek olması ve sondan eklemeli bir dil olması, kural tabanlı çözüm yollarını zayıflatmaktadır. Modelin bu vurguyu doğru tespit etmesi; metinden konuşmaya sistemlerinde daha doğal vurgu üretimi, duygu analizi ve niyet analizi görevlerinde daha hassas anlam çıkarımı ve bağlama uygun cevap üreten sohbet sistemleri için önemlidir.

## 2.2 Ön Rapor Stratejisi ve Finalde Yapılan Düzeltmeler

Ön rapor aşamasında hibrit veri stratejisi olarak büyük ölçüde sentetik BIO etiketli veri ile birlikte ek bir gerçek dünya gürültülü veri kümesi kullanılması planlanmıştır. İlk taslakta Kaggle üzerindeki bir sentiment veri seti referans alınmış olsa da, final uygulama aşamasında **erişilebilirlik, tekrar üretilebilirlik ve doğrudan entegrasyon kolaylığı** nedenleriyle kamuya açık ve programatik olarak çekilebilen Hugging Face Türkçe veri kümeleri tercih edilmiştir. Bu değişiklik, ön rapordaki planın bir düzeltmesi ve iyileştirmesi olarak yapılmıştır.

## 2.3 Kullanılan Veri Kaynakları

### 2.3.1 Sentetik / Önceki Aşama Verisi

Projede eğitimin çekirdeğini oluşturan sentetik veri, önceki proje aşamasında oluşturulan Türkçe pragmatik vurgu örneklerinden gelmektedir.

- Kaynak CSV kümeleri: `vurgu_varyasyonlari.csv`, `vurguHece.csv`
- Başlangıç düzeyi toplam örnek: `6,253`
- Temizleme sonrası kullanılabilir örnek: `5,209`
- Etiketleme biçimi: `BIO` (`O`, `B-EMPHASIS`, `I-EMPHASIS`)

### 2.3.2 Gerçek / OOD Veri

Final çalışmada, dağılım dışı dayanıklılığı sınamak için iki kamuya açık Türkçe veri kaynağından örnekleme yapılmıştır:

- `maydogan/Turkish_SentimentAnalysis_TRSAv1`
- `yankihue/tweets-turkish`

Bu kaynaklardan toplam `1,000` cümle seçilmiş ve proje veri şemasına dönüştürülmüştür.

| Kaynak | Örnek Sayısı | Alan |
| --- | ---: | --- |
| TRSA yorumları | 700 | E-ticaret yorumları |
| Türkçe tweetler | 300 | Sosyal medya |

## 2.4 Final Veri Ayrımı

Temizlenmiş sentetik veri aşağıdaki şekilde bölünmüştür:

| Bölüm | Örnek Sayısı |
| --- | ---: |
| Train | 3,646 |
| Validation | 781 |
| Test | 782 |

OOD kümesi ayrıca değerlendirme için tutulmuştur:

| Bölüm | Örnek Sayısı |
| --- | ---: |
| OOD Test | 1,000 |

**Önemli not:** OOD kümesindeki vurgu etiketleri şu anda `auto_suggested` olarak işaretlidir. Bu nedenle final raporda açık sınırlama olarak belirtilmiştir.

---

# 3. Derin Öğrenme Modelinin Oluşturulması

## 3.1 Nihai Seçilen Mimarî

Final uygulama için ana model aşağıdaki topolojiye sahiptir:

`Input -> Tokenizer -> BERTurk -> [CLS] branch -> SCL head -> token branch -> CRF -> BIO output`

Bu mimari `models/bert_crf.py` dosyasında gerçeklenmiştir.

![Bölüm 3 mimarisi](outputs/results/final_sections_3_8/section3_topology.png){ width=95% }

## 3.2 Katmanlar ve Özellikleri

### 3.2.1 Tokenizer ve Girdi

- Türkçe kelime dizisi girdi olarak alınır.
- Alt-kelime parçalama için BERT tabanlı tokenizer kullanılır.
- Maksimum sekans uzunluğu: `128`

### 3.2.2 Encoder

- Omurga model: `dbmdz/bert-base-turkish-cased`
- Katman sayısı: `12`
- Hidden size: `768`
- Toplam parametre sayısı: yaklaşık `110.8M`

### 3.2.3 Contrastive Dal

Bu dal yalnızca `[CLS]` temsilini kullanır. Böylece cümle düzeyinde vurgu örüntüsü ayrıştırılmaya çalışılır.

- Projection head: `768 -> 256 -> 128`
- Aktivasyon: `GELU`
- Dropout: `0.1`
- L2 normalizasyon: aktif
- Temperature: `0.07`
- Loss weight: `0.2`

Contrastive sınıflar:

- `0`: vurgu yok
- `1`: tek kelimelik vurgu
- `2`: çok kelimelik vurgu (`I-EMPHASIS` içerir)

### 3.2.4 Token Sınıflandırma Dalı

- Token hidden state girdi olarak alınır.
- `Dropout(0.1)` uygulanır.
- `Linear(768, 3)` emission head ile üç BIO etiketi için skor üretilir.

### 3.2.5 CRF Katmanı

CRF katmanı BIO etiket dizisinin yapısal tutarlılığını korur.

Başlatılan geçiş kuralları:

- `O -> I = -10.0`
- `start(I) = -10.0`
- `B -> I = +2.0`
- `I -> I = +1.0`

## 3.3 Kayıp Fonksiyonu

Nihai kayıp fonksiyonu:

`L_total = L_crf + 0.2 * L_scl`

Burada:

- `L_crf`: yapılandırılmış etiket dizisi kaybı
- `L_scl`: `[CLS]` temsili üzerinde denetimli karşıtlamalı kayıp

---

# 4. Deneysel Çalışmalar

## 4.1 Eğitim Koşulları

Final deneyler Apple Silicon üzerinde `mps` hızlandırması ile yürütülmüştür.

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

## 4.2 Kullanılan Ölçütler

Başarı değerlendirmesinde aşağıdaki metrikler kullanılmıştır:

- Weighted F1
- Macro F1
- Precision
- Recall
- `I-EMPHASIS` sınıfı için özel F1 ve recall
- Confusion matrix

## 4.3 Ana Test Sonuçları

| Model | Weighted F1 | Macro F1 | Precision | Recall | I-EMPHASIS F1 | I-EMPHASIS Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline CE | 0.8820 | 0.6607 | 0.8877 | 0.8938 | 0.4375 | 0.3333 |
| BERT+CRF+SCL | 0.8842 | 0.7026 | 0.8888 | 0.8951 | 0.5556 | 0.4762 |

## 4.4 OOD Sonuçları

| Model | Weighted F1 | Macro F1 | Precision | Recall | I-EMPHASIS F1 | I-EMPHASIS Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline CE | 0.8500 | 0.3181 | 0.8153 | 0.8937 | 0.0000 | 0.0000 |
| BERT+CRF+SCL | 0.8487 | 0.3196 | 0.8156 | 0.8898 | 0.0000 | 0.0000 |

## 4.5 Azınlık Sınıfı Analizi

Azınlık sınıfı olan `I-EMPHASIS`, çok-kelimeli vurgu bölgelerini temsil ettiği için bu proje açısından en kritik sınıftır.

![I-EMPHASIS karşılaştırması](outputs/results/final_sections_3_8/section4_i_emphasis_focus.png){ width=90% }

Bu sonuçlar, yeni modelin genel weighted F1 kazanımının sınırlı olmasına rağmen, araştırma açısından daha değerli olan azınlık sınıfı başarımında anlamlı iyileşme sağladığını göstermektedir.

## 4.6 Görsel Çıktılar

### Baseline CE Test Confusion Matrix

![Baseline CE confusion matrix](outputs/results/baseline_ce/test/confusion_matrix.png){ width=78% }

### BERT+CRF+SCL Test Confusion Matrix

![BERT+CRF+SCL confusion matrix](outputs/results/test/confusion_matrix.png){ width=78% }

## 4.7 Sonuç Yorumu

Deneyler göstermektedir ki:

- İki modelin toplam test weighted F1 skorları birbirine yakındır.
- `BERT+CRF+SCL`, `I-EMPHASIS` üzerinde daha güçlüdür.
- OOD değerlendirmesi anlamlı bir stres testi sağlamış, ancak final yayın kalitesinde sonuç için OOD etiketlerinin manuel audit edilmesi gereklidir.

---

# 5. İyileştirme ve Karşılaştırma

Bu bölüm `DL_25_v3` gereği **GenAI’dan bağımsız** biçimde yürütülen model iyileştirme ve karşılaştırma deneylerini sunmaktadır.

## 5.1 Legacy Cross-Entropy ile Yeni Model Karşılaştırması

| Model | Weighted F1 | Macro F1 | I-EMPHASIS F1 | I-EMPHASIS Recall |
| --- | ---: | ---: | ---: | ---: |
| Baseline CE | 0.8820 | 0.6607 | 0.4375 | 0.3333 |
| BERT+CRF+SCL | 0.8842 | 0.7026 | 0.5556 | 0.4762 |

Sayısal farklar:

- Weighted F1 farkı: `+0.0022`
- `I-EMPHASIS` F1 farkı: `+0.1181`
- `I-EMPHASIS` recall farkı: `+0.1429`

## 5.2 Hiperparametre Tuning Tablosu

| Konfigürasyon | Dropout | Head LR | Val Weighted F1 | Val I-EMPHASIS F1 |
| --- | ---: | ---: | ---: | ---: |
| default | 0.1 | 1e-4 | 0.8799 | 0.5938 |
| dropout=0.2 | 0.2 | 1e-4 | 0.8723 | 0.4762 |
| head_lr=5e-5 | 0.1 | 5e-5 | 0.8759 | 0.6250 |

![Hyperparameter sweep](outputs/results/final_sections_3_8/section5_hyperparameter_sweep.png){ width=90% }

## 5.3 BERT2D Pilot Karşılaştırması

| Model | Epoch | Weighted F1 | Macro F1 | I-EMPHASIS F1 | I-EMPHASIS Recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| BERT2D+CRF+SCL pilot | 1 | 0.8737 | 0.6191 | 0.3636 | 0.2222 |

Bu pilot, BERT2D’nin pratikte entegre edilebilir olduğunu göstermiştir; ancak kendi uzak kodu `word_ids` ve `subword_ids` için default üretim uyarıları verdiğinden final ana model olarak seçilmemiştir.

## 5.4 Hazır Kod ve Özgün Kod Ayrımı

### Kütüphane Tabanlı Bileşenler

- Hugging Face Transformers
- `torchcrf`
- `sklearn`
- `matplotlib` / `seaborn`

### Projeye Özgü Kodlar

- `[CLS]` tabanlı supervised contrastive loss
- Projection head entegrasyonu
- OOD veri oluşturma ve örnekleme hattı
- Ayrık baseline ve CRF+SCL eğitim scriptleri
- Karşılaştırma artefact üreticileri

---

# 6. Araştırma: Kod Üretmede Gen AI

`DL_25_v3` gereği bu bölümde kod üretmede güçlü GenAI araçları ve güçlü yönleri özetlenmiştir.

## 6.1 GPT-4o / GPT-4.1 Ailesi

- PyTorch ve Hugging Face ekosistemi için hızlı taslak üretir.
- Refactoring, açıklama ve yardımcı fonksiyon yazmada etkilidir.
- Risk: tensor boyutlarını bazen yanlış varsayabilir.

## 6.2 Claude 3.5 / 3.7 Ailesi

- Uzun bağlamı iyi okur ve hata analizi yapar.
- Açıklamalı reasoning ve kod gözden geçirmede etkilidir.
- Risk: bazı matematiksel detayları anlatıp implementasyonda eksik bırakabilir.

## 6.3 Gemini 1.5 / 2.x Ailesi

- Uzun belge sentezi ve veri üretimi görevlerinde güçlüdür.
- Çok belgeli araştırma özetlerinde pratiktir.
- Risk: son derin öğrenme kodu yine auditor kontrolü gerektirir.

## 6.4 Genel Yorum

Kod üretmede tek bir “en iyi model” yoktur. Farklı araçlar farklı alt görevlerde iyidir. Ancak derin öğrenme projelerinde özellikle tensor şekilleri, maskeleme ve loss reduction mantığı için insan denetimi zorunludur.

---

# 7. Gen AI Desteği ile İyileştirme

Bu bölümde GenAI destekli iyileştirme süreci bir “blind trust” biçiminde değil, denetlenmiş bir geliştirme akışı olarak ele alınmıştır.

## 7.1 Prompt 1: GPT-4o Tarzı SCL İsteği

```text
Write a PyTorch supervised contrastive loss for sentence classification.
Input embeddings are BxLxH token embeddings from BERT.
Use labels of shape B and return one scalar loss.
```

### Simüle Edilmiş Hatalı Çıktı

```python
def scl_loss(token_embeddings, labels, temperature=0.07):
    features = F.normalize(token_embeddings, dim=-1)
    logits = torch.matmul(features, features.T) / temperature
    positive_mask = labels.unsqueeze(0) == labels.unsqueeze(1)
    log_prob = logits - torch.log(torch.exp(logits).sum(dim=1, keepdim=True))
    loss = -(positive_mask * log_prob).sum(dim=1) / positive_mask.sum(dim=1)
    return loss.mean()
```

### Auditor Bulguları

1. `B x L x H` tensörü yanlış biçimde `B x H` gibi kullanılmıştır.
2. Rank-3 tensor için `features.T` uygun değildir.
3. Self-pair mask eksiktir.
4. Pozitif çift içermeyen satırlarda bölüm hatası vardır.

### Uygulanan Düzeltme

- Contrastive dal yalnızca `[CLS]` üzerinde çalışacak şekilde yeniden tasarlandı.
- Diyagonal açıkça maskelendi.
- Pozitif çift sayısı sıfır olan satırlar ortalamaya alınmadı.

## 7.2 Prompt 2: Claude 3.5 Tarzı Debug İsteği

```text
Rewrite the SCL loss to work inside a BERT+CRF token classifier.
The contrastive branch should focus on minority emphasis patterns and be robust when a batch contains only one class.
```

### Simüle Edilmiş Hatalı Çıktı

```python
def scl_loss(cls_embeddings, labels):
    sim = cls_embeddings @ cls_embeddings.t()
    mask = labels == labels.T
    sim = sim / 0.07
    exp_sim = torch.exp(sim)
    return -torch.log((exp_sim * mask).sum() / exp_sim.sum())
```

### Auditor Bulguları

1. `labels == labels.T` yanlış broadcast varsayımı içerir.
2. Batch geneli tek oranla özetlenmiş, anchor bazlı mantık kaybolmuştur.
3. `L2` normalizasyon eksiktir.
4. Self-pair’ler sistemden çıkarılmamıştır.

## 7.3 Özet Sonuç Tablosu

| İşlem | Derin Öğrenme Modeli Özellikleri | Deneyim / Auditor Notu | Başarı Değeri |
| --- | --- | --- | --- |
| Legacy baseline | BERTurk + CrossEntropy | Referans model | Test weighted F1 = 0.8820 |
| CRF entegrasyonu | BERTurk + CRF | BIO yapısal tutarlılık | Yapısal iyileşme |
| SCL entegrasyonu | BERTurk + CRF + CLS-SCL | Azınlık sınıf temsili güçlendi | Test I-EMPHASIS F1 = 0.5556 |
| GPT-4o tarzı taslak | Hatalı tensor şekli varsayımı | Auditor müdahalesi zorunlu | Doğrudan kullanılmadı |
| Claude 3.5 tarzı taslak | Hatalı mask/reduction | Auditor sonrası yararlı | Nihai loss tasarımına katkı |
| BERT2D pilotu | BERT2D + CRF + SCL | Uyarılar sebebiyle pilot | Test weighted F1 = 0.8737 |

## 7.4 Genel Değerlendirme

GenAI burada başarıyı tek başına artırmamıştır. Asıl katkı, tasarım alanını hızla genişletmesi ve auditor’un doğru çözümü daha hızlı bulmasına yardımcı olmasıdır.

---

# 8. Evaluator / Auditor Rolü

## 8.1 Neden Auditor / Evaluator Rolü Önemli Hale Geldi?

GenAI araçlarının kod üretme kapasitesi arttıkça, öğrenciyi yalnızca kod yazan kişi olarak konumlandırmak yetersiz hale gelmiştir. Çünkü günümüzde bir model, kısa sürede çok miktarda kod üretebilir; fakat bu kodun doğruluğu, deneysel geçerliliği ve bilimsel savunulabilirliği garanti edilmez. Bu nedenle eğitimde öğrencinin giderek daha fazla **karar verici**, **değerlendirici** ve **denetçi** konumuna yerleştirilmesi önemlidir.

Bu projede auditor rolü şu alanlarda belirleyici olmuştur:

1. `[CLS]` temelli contrastive dalın seçilmesi
2. Tensor şekillerinin doğrulanması
3. ID ve OOD deney protokolünün ayrılması
4. Gerçek metriklerin eski abartılı anlatıların yerine geçirilmesi
5. BERT2D ve OOD etiketleri için risklerin açıkça raporlanması

## 8.2 Proje Odaklı Öğrenme Prompt’u

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
7. Annotate all tensor shapes explicitly.
```

## 8.3 Kısa Cevap / Öğrenme Notu

Bu promptun beklenen ana cevabı, sağlıklı bir temsil uzayında `0`, `1` ve `2` sınıflarının ayrık kümeler oluşturması; özellikle `I-EMPHASIS` içeren `2` sınıfının en zor ve en kırılgan azınlık kümesi olması gerektiğidir. Eğer weighted F1 yüksek kalırken `I-EMPHASIS` recall düşüyorsa, model çoğunluk sınıfına yaslanıyor demektir. Bu nedenle sadece toplam başarı değil, azınlık sınıf metrikleri de birlikte izlenmelidir.

---

# 9. Özdeğerlendirme Tablosu

| Madde | Puan | Var | Açıklama | Tahmini Puan |
| --- | ---: | --- | --- | ---: |
| Model Hakkında Araştırma | 5 | Evet | BERT, CRF, SCL, BERT2D ve Türkçe encoder literatürü incelendi | 5 |
| Veri Seti ve Konu Belirleme | 5 | Evet | Sentetik + gerçek/OOD hibrit veri stratejisi kuruldu | 5 |
| Derin Öğrenme Modelinin Oluşturulması | 15 | Evet | BERT+CRF+SCL modeli kodlandı ve topolojisi verildi | 15 |
| Deneysel Çalışmalar | 15 | Evet | Train/val/test/OOD deneyleri ve görseller üretildi | 15 |
| İyileştirme ve Karşılaştırma | 10 | Evet | Baseline, tuning ve BERT2D pilot karşılaştırması yapıldı | 10 |
| Araştırma: Kod Üretmede Gen AI | 10 | Evet | GenAI modellerinin güçlü yönleri özetlendi | 10 |
| Gen AI Desteği ile İyileştirme | 10 | Evet | Promptlar, hatalar, auditor düzeltmeleri ve özet tablo eklendi | 10 |
| Karar verici ve denetçi rolü sorusu ve cevabı | 10 | Evet | Auditor refleksiyonu ve proje odaklı prompt eklendi | 10 |
| Özdeğerlendirme Tablosu, Rapor ve Kaynakça | 20 | Evet | Birleşik nihai rapor, kaynakça ve ekler tamamlandı | 20 |
| **Toplam** | **100** |  |  | **100** |

---

# 10. Kaynakça

1. Devlin, J. et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.
2. Liu, Y. et al. (2019). RoBERTa: A Robustly Optimized BERT Pretraining Approach.
3. Lample, G. et al. (2016). Neural Architectures for Named Entity Recognition.
4. Gunel, B. et al. (2021). Supervised Contrastive Learning for Pre-trained Language Model Fine-tuning.
5. Schweter, S. (2020). BERTurk - BERT models for Turkish.
6. Dehghan, M., & Amasyalı, M. F. (2025). A Turkish Dataset and BERTurk-Contrastive Model for Semantic Textual Similarity.
7. Scheible-Schmitt, R., & Schweter, S. (2025). SindBERT: A Large-Scale RoBERTa-Based Encoder for Turkish.
8. Yılmaz, Y. et al. (2025). BERT2D: Positional Embeddings for Morphologically Rich Languages.
9. Umer, S. (2024). Sentiment Dataset – Positive & Negative Texts Data.
10. `DL_25_v3.docx`, Ege Üniversitesi Derin Öğrenme Proje Yönergesi.

---

# 11. Ekler: Teslime Dahil Edilen Kod ve Dosyalar

## 11.1 Temel Kaynak Kodlar

- `config.py`
- `data_loader.py`
- `train_v2.py`
- `baseline_train.py`
- `evaluation.py`
- `compare_models.py`
- `run_pipeline.py`
- `token-classification.py`
- `sentetic-data.py`
- `generate_sections_3_8_assets.py`

## 11.2 Model Modülleri

- `models/bert_crf.py`
- `models/weighted_loss.py`
- `models/__init__.py`

## 11.3 Veri Artırma ve Yardımcı Modüller

- `data_augmentation/schema.py`
- `data_augmentation/focus_shifting.py`
- `data_augmentation/morphological.py`
- `data_augmentation/downsampling.py`

## 11.4 Veri ve Sonuç Dosyaları

- `data/processed/train.json`
- `data/processed/val.json`
- `data/processed/test.json`
- `data/processed/ood_test.json`
- `outputs/results/train_v2_results.json`
- `outputs/results/baseline_ce/summary.json`
- `outputs/results/comparisons/model_comparison.csv`
- `outputs/results/final_sections_3_8/`

## 11.5 Sunum ve Teslim Yardımcıları

- `Proje-final-raporu.docx`
- `Presentation_Slides_Outline.md`
- `Submission_Checklist.md`
- `DL25_v3_uyum_kontrolu.docx`

---

# Sonuç

Bu birleşik nihai rapor, ön raporun araştırma ve problem tanımı çerçevesini koruyarak final uygulama aşamasındaki gerçek kod, gerçek deney, karşılaştırma, GenAI audit süreci ve auditor refleksiyonunu tek belgede bütünleştirmiştir. Çalışmanın temel katkısı, Türkçe pragmatik vurgu tespiti için yürütülen sequence labeling görevinde `BERT+CRF+SCL` yapısının özellikle azınlık sınıfı olan `I-EMPHASIS` üzerinde legacy çapraz entropi tabanlı modele göre daha güçlü performans göstermesidir. Bu durum, yalnızca toplam başarımın değil, azınlık sınıf dayanıklılığının da araştırma değerini belirlediğini göstermektedir.
