---
marp: true
theme: metropolis-ege
paginate: true
size: 16:9
header: 618 Derin Öğrenme | Proje 2 Sunumu (Presentation II)
footer: Burak YÖRÜK | Türkçe Pragmatik Vurgu Tespiti
---

<!-- _class: lead -->

# Türkçe Pragmatik Vurgu Tespiti
## `BERT+CRF+SCL` ile OOD(Out-of-Distribution) Sağlamlık Analizi

**Proje 2 Sunumu (Presentation II)**  
Burak YÖRÜK  
Ege Üniversitesi, Bilgisayar Mühendisliği


---

# Problem ve Motivasyon

- Yazılı Türkçe, sözlü prosodiyi(konuşma ezgisi) doğrudan taşımaz.
- Pragmatik vurgu; **TTS**, **duygu analizi** ve **sohbet sistemleri** için kritiktir.
- Türkçede:
  - sözcük sırası esnek,
  - morfoloji zengin,
  - vurgu kural tabanlı olarak güvenilir modellenemez.
- Bu yüzden, **token-level deep learning** ile problemin ele alınması gerekir.

---

# Literatür Taraması: Temel Mimariler

<div class="two-col">
<div>

## 1. BERTurk (Schweter, 2020)
- **Neden Gerekli?** Türkçe sondan eklemeli bir dildir. mBERT (çok dilli) modeller, kelime köklerini (subword) parçalamada yetersiz kalır.
- **Katkısı:** 32 milyar token ile Türkçeye özel eğitilmiştir. Projede güçlü bir *özellik çıkarıcı (feature extractor)* olarak kullanılmıştır.

</div>
<div>

## 2. CRF ile NER (Lample vd., 2016)
- **Neden Gerekli?** Softmax, "O" (Vurgusuz) etiketinden sonra kural dışı olarak "I-EMPHASIS" üretebilir.
- **Katkısı:** CRF (Conditional Random Fields), Viterbi algoritması ile global etiket tutarlılığını sağlar. Projemizde sıralı BIO bütünlüğünü garanti eder.

</div>
</div>

---

# Literatür Taraması: Sınıf Dengesizliği

## 3. Supervised Contrastive Learning (Gunel vd., 2021)
- **Problem:** Veri setimizde **%96** "O" (Vurgusuz), **%4** "I-EMPHASIS" (Vurgulu) token bulunmaktadır. Standart *Cross-Entropy* kayıp fonksiyonu çoğunluk sınıfına fazla meyleder.
- **Çözüm:** Aynı sınıftaki (örn: vurgulu) örneklerin temsillerini uzayda birbirine yaklaştıran, farklı olanları uzaklaştıran SCL yaklaşımı.
- **Projedeki Rolü:** SCL, sadece `[CLS]` token'ı üzerinden uygulanarak azınlık sınıfı F1 skorunda belirgin sıçrama (`0.43 -> 0.55`) yaratmıştır.



---

# Literatür Taraması: Güncel Türkçe Yaklaşımlar

<div class="two-col">
<div>

## 4. BERTurk-contrastive (Dehghan & Amasyalı, 2025)
- **Odak Noktası:** Contrastive Learning (Karşıtlamalı Öğrenme) tekniğinin doğrudan Türkçe dil modellerine uyarlanması.
- **Katkısı:** Modelin uzayında anlamsal temsilleri daha homojen ayırarak vektör kalitesini artırır.
- **Projedeki Rolü:** Özel olarak entegre ettiğimiz `SCL` (Supervised Contrastive Learning) kaybının (loss) Türkçe metinlerdeki "Vurgulu/Vurgusuz" sınıf ayrımı konusundaki başarısını literatürde destekleyen en güncel referanstır.

</div>
<div>

## 5. BERT2D (Yılmaz vd., 2025)
- **Odak Noktası:** Kelime (word) ve alt-kelime (subword) ilişkilerini iki boyutlu bir yapıda modelleyen yeni nesil bir mimari.
- **Katkısı:** Sondan eklemeli dillerdeki (Türkçe gibi) tokenizasyon bilgi kaybını azaltmayı hedefler.
- **Projedeki Rolü:** Projede **pilot model** olarak entegre edilip test edilmiştir (Pilot Macro F1: 0.6191). Ancak `word_ids / subword_ids` hizalama (alignment) uyarıları nedeniyle ana model seçilmemiş, gelecek adımlar için güçlü bir alternatif olarak bırakılmıştır.

</div>
</div>

---

# Uygulama: Kod Nasıl Çalışıyor? (Custom Loss)

Modelin eğitim döngüsündeki **ikili kayıp (dual-loss)** mimarisi (`models/bert_crf.py`):

```python
# 1. BERT'ten Temsillerin (Embeddings) Alınması
outputs = self.bert(...)
seq_out = outputs[0]               # Token bazlı (CRF için)
cls_out = seq_out[:, 0]            # [CLS] token'ı (SCL için)

# 2. CRF Loss Hesaplanması (Viterbi Decoding ile)
emissions = self.classifier(seq_out)
loss_crf = -self.crf(emissions, labels, mask=attention_mask, reduction='mean')

# 3. Supervised Contrastive (SCL) Loss Hesaplanması
loss_scl = self.scl_loss_fn(cls_out, labels_cls)

# 4. Kayıpların Birleştirilmesi (alpha = 0.2 hiperparametresi ile)
total_loss = loss_crf + (self.alpha * loss_scl)
```

---

# Canlı Demo: Model Gerçekte Nasıl Çalışır?

Modelin eğitimde **hiç görmediği** bir cümlede çıkarım (inference) adımları:

<div class="two-col">
<div>

## 1. Girdi ve Tokenizasyon
`> "Bu akşam sinemaya gideceğiz, değil mi?"`

*Model bu cümleyi parçalara (subwords) ayırır:*
`[ Bu, akşam, sine, ##maya, ... ]`

</div>
<div>

## 2. Çıktı ve Vurgu Tespiti
*Terminal veya Web arayüzü çıktısı:*
`Bu akşam ` <span style="color:#d32f2f; font-weight:bold;">*sinemaya*</span> ` gideceğiz, değil mi?`

**Sonuç:** Model, bağlamı (attention) anlayarak, hedeflenen kelimedeki pragmatik vurguyu CRF ve BIO etiketleri (B-EMPH, I-EMPH) ile başarıyla tespit eder.

</div>
</div>

---

# Araştırma Sorusu

Yapay zeka dersi kapsamında başlatılan Turkish Stress Detection - LLM Token Classification
konusu Türkçe Dizilim Etiketleme (Sequence Labeling) Görevlerinde Gözetimli Karşıtlamalı
Öğrenme (Supervised Contrastive Learning) Destekli Büyük Dil Modelleri: 
Pragmatik Vurgu Tespiti Üzerine Dağılım Dışı (OOD) Sağlamlık Analizi kapsamında devam ettirilmektedir.

- `BERT` tabanlı bir sequence labeling modeli Türkçe pragmatik vurguyu öğrenebilir mi?
- `CRF(Conditional Random Fields)`, BIO etiket tutarlılığını anlamlı biçimde artırır mı?
- `[CLS]` üzerinde çalışan **Supervised Contrastive Learning(SCL)**, azınlık sınıfı olan `I-EMPHASIS` için fayda sağlar mı?
- Model, gerçek ve gürültülü Türkçe metinlerde ne kadar dayanıklıdır?

---

# Veri Stratejisi

<div class="two-col">
<div>

## Sentetik / ID Veri

- Önceki aşamadan gelen BIO etiketli veri
- Temizleme sonrası kullanılabilir örnek: **5,209**
- Bölümleme:
  - Train: **3,646**
  - Val: **781**
  - Test: **782**

</div>
<div>

## Gerçek / OOD Veri

- Toplam: **1,000** cümle
- Kaynaklar:
  - **700** TRSA yorumları
  - **300** Türkçe tweet
- Durum: `auto_suggested`
- Amaç: dağılım dışı dayanıklılığı test etmek

</div>
</div>

<div class="caption">Uygulamada tekrar üretilebilirlik için programatik olarak erişilebilen kamuya açık Türkçe veri kümeleri kullanıldı.</div>

---

# Nihai Mimari

`Input -> Tokenizer -> BERTurk -> [CLS] branch -> SCL head -> token branch -> CRF -> BIO output`

![w:1100 rounded](assets/section3_topology.png)

---

# Neden CRF + SCL?

<div class="two-col">
<div>

## CRF

- BIO etiket dizisini yapısal olarak düzenler
- `O -> I` gibi anlamsız geçişleri cezalandırır
- Özellikle çok-kelimeli vurgu span'larında faydalıdır

</div>
<div>

## SCL

- `[CLS]` üzerinden cümle temsillerini ayrıştırır
- `vurgu yok / tek kelime / çok kelime` örüntülerini ayırmaya çalışır
- Azınlık sınıfı için temsil kalitesini artırmayı hedefler

</div>
</div>

---

# Eğitim Kurulumu

| Parametre | Değer |
| --- | --- |
| Backbone | `dbmdz/bert-base-turkish-cased` |
| Batch size | `8` |
| Epoch | `3` |
| Encoder LR | `2e-5` |
| Head LR | `1e-4` |
| Dropout | `0.1` |
| SCL temperature | `0.07` |
| Loss | `L_total = L_crf + 0.2 * L_scl` |
| Device | `mps` |

---

# Ana Test Sonuçları

<div class="metric-card-wrap">
<div class="metric-card">
<h3>Baseline CE Weighted F1</h3>
<p>0.8820</p>
</div>
<div class="metric-card">
<h3>BERT+CRF+SCL Weighted F1</h3>
<p>0.8842</p>
</div>
<div class="metric-card">
<h3>Baseline I-EMPHASIS F1</h3>
<p>0.4375</p>
</div>
<div class="metric-card">
<h3>BERT+CRF+SCL I-EMPHASIS F1</h3>
<p>0.5556</p>
</div>
</div>

- Toplam weighted F1 kazanımı küçük
- **Gerçek katkı:** `I-EMPHASIS` azınlık sınıfındaki belirgin artış

---

# Azınlık Sınıfı Kazanımı

![w:820 rounded](assets/section4_i_emphasis_focus.png)

- `I-EMPHASIS` F1: **0.4375 -> 0.5556**
- `I-EMPHASIS` recall: **0.3333 -> 0.4762**

<div class="caption">Bu proje için en kritik metrik, toplam başarıdan çok azınlık sınıfının toparlanmasıdır.</div>

---

# Hiperparametre Tuning

![w:820 rounded](assets/section5_hyperparameter_sweep.png)

- `dropout = 0.2` azınlık sınıf performansını düşürdü
- `head_lr = 5e-5` makul ama final yapı kadar güçlü değil
- Seçilen final ayar: **dropout 0.1 / head LR 1e-4**

---

# Karşılaştırmalı Sonuç Özeti

| Model | Test Weighted F1 | Test Macro F1 | I-EMPHASIS F1 | I-EMPHASIS Recall |
| --- | ---: | ---: | ---: | ---: |
| Baseline CE | 0.8820 | 0.6607 | 0.4375 | 0.3333 |
| BERT+CRF+SCL | 0.8842 | 0.7026 | 0.5556 | 0.4762 |
| BERT2D+CRF+SCL pilot | 0.8737 | 0.6191 | 0.3636 | 0.2222 |

- BERT2D entegre edildi ve çalıştırıldı
- Ancak `word_ids / subword_ids` uyarıları nedeniyle final ana model seçilmedi

---

# OOD ve Audit Bulguları

<div class="two-col">
<div>

## OOD

- Baseline OOD weighted F1: **0.8500**
- Joint model OOD weighted F1: **0.8487**
- OOD azınlık F1: **0.0**
- Ana neden: OOD etiketleri henüz manuel audit edilmedi

</div>
<div>

## GenAI Audit

- GPT-4o tarzı çıktı: tensor shape hatası
- Claude tarzı çıktı: mask / reduction hatası
- İnsan auditor düzeltti:
  - CLS-only contrastive branch
  - diagonal masking
  - zero-positive handling
  - stable environment pinning

</div>
</div>

---

# Sonuç

- **Final en iyi pratik model:** `BERT+CRF+SCL`
- Genel weighted F1 artışı sınırlı ama istikrarlı
- En anlamlı katkı: **`I-EMPHASIS` azınlık sınıfında iyileşme**
- Projenin ikinci ana katkısı: **denetlenebilir, tekrar üretilebilir ve auditor odaklı geliştirme hattı**

---

# Sınırlılıklar ve Sonraki Adımlar

- OOD kümesinin manuel audit edilmesi gerekiyor
- BERT2D için daha derin entegrasyon yapılabilir
- Gerçek Türkçe vurgu anotasyonlu daha büyük veri kümesi toplanabilir
- UMAP / t-SNE ile SCL uzayı ayrıca görselleştirilebilir

---

<!-- _class: lead -->

# Teşekkürler

Ek materyaller, proje dosyaları ile paylaşılmıştır.**

---

# Kaynaklar

<div class="two-col tiny">
<div>

## Makaleler

- Devlin et al. (2019), **BERT**
- Liu et al. (2019), **RoBERTa**
- Lample et al. (2016), **Neural Architectures for NER**
- Gunel et al. (2021), **Supervised Contrastive Learning**
- Schweter (2020), **BERTurk**
- Dehghan & Amasyalı (2025), **BERTurk-contrastive**
- Yılmaz et al. (2025), **BERT2D**

</div>
<div>

## Veri Setleri ve Modeller

- `maydogan/Turkish_SentimentAnalysis_TRSAv1`
- `yankihue/tweets-turkish`
- `dbmdz/bert-base-turkish-cased`
- `yigitbekir/Bert2D-cased-Turkish-128K-WWM-NSW2`

## Proje Belgeleri

- `DL_25_v3.docx`
- `Proje-updated-rapor1.pdf`
- `Proje-final-raporu.docx`

</div>
</div>
