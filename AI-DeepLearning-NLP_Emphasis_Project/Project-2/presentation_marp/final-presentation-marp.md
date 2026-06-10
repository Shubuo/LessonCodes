---
marp: true
theme: metropolis-ege
paginate: true
size: 16:9
header: 618 Derin Öğrenme | Proje 1 Sunumu
footer: Burak YÖRÜK | Türkçe Pragmatik Vurgu Tespiti
---

<!-- _class: lead -->

# Türkçe Pragmatik Vurgu Tespiti
## `BERT+CRF+SCL` ile OOD(Out-of-Distribution) Sağlamlık Analizi

**Proje 1 Sunumu**  
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

# Araştırma Sorusu


Yapay zeka dersi kapsamında başlatılan 
- Turkish Stress Detection - LLM Token Classification çalışması
- Türkçe Dizilim Etiketleme (Sequence Labeling) Görevlerinde Gözetimli Karşıtlamalı
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

Ek materyaller, proje dosyaları ile paylaşılmıştır.

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
- Yörük, B., & Kaçıkan, E. (2024). Türkçe Metinlerde Pragmatik Vurgunun Belirlenmesi, Yapay Zeka Dersi Projesi Raporu, Ege Üniversitesi.

</div>
<div>

## Veri Setleri ve Modeller

- `maydogan/Turkish_SentimentAnalysis_TRSAv1`
- `yankihue/tweets-turkish`
- `dbmdz/bert-base-turkish-cased`
- `yigitbekir/Bert2D-cased-Turkish-128K-WWM-NSW2`

</div>
</div>
