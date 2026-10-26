# Complex Network Analysis of UAV Swarms — Plan

Ders: Algorithms for Complex Networks (Ege Ü., Doç. Dr. Züleyha Akusta Dağdeviren)
Sunum 1: **2 Kasım 2026 Pzt, 13:15** · Notlandırma: Sunum 1 %20, Sunum 2 %20, Final Proje %60 (kod + rapor + demo)

## Hedef ve başarı kriterleri

- Türkçe, 16 slaytlık `.pptx` (+ PDF yedeği); 15 dk ana akış + 5 dk soru.
- Her sayısal iddia ve figür makalede sayfa/şekil numarasıyla doğrulanmış.
- Konu dokümanındaki 5 odak görünür: dinamik graf modeli, topoloji/bağlantılılık, merkezilik ve kritik İHA'lar, düğüm/bağlantı hatalarına dayanıklılık, endüstriyel denetim.
- Slayt 16, final projeye dönüşebilecek kodlanabilir bir araştırma sorusuna köprü kurar.

Kapsam dışı: Sunum 2 içeriği, final proje kodu, Meshine veri izinleri.

## Kararlar

| Konu | Karar |
| --- | --- |
| Dil | Tamamen Türkçe; terimlerin İngilizcesi ilk geçişte parantez içinde |
| Araç | python-pptx (düzenlenebilir), figürler NetworkX/matplotlib |
| Kapalı erişim (P1, P4) | Kullanıcı indirdi → `Alg4ComplexNtw/papers/` |
| Meshine | Sunum 1'de motivasyon; Sunum 2'de telemetri veri adayı (izin + anonimleştirme gerekli) |
| Ek zip (6 makale) | Kullanılmıyor: 2019–2022, kontrol/kalabalık/AUV odaklı, ağ analizi yok |
| İnfografik (Drone Industry Insights 2024) | Telifli; slayt 5'teki kontrol mimarileri için ilham, kendi çizimimiz + atıf |

## Makaleler

| # | Yıl | Makale | DOI | Erişim |
| --- | --- | --- | --- | --- |
| P1 | 2022 | Alam et al. — Topology control algorithms in multi-UAV networks: An extensive survey (JNCA 207) | 10.1016/j.jnca.2022.103495 | Kapalı (indirildi) |
| P2 | 2024 | Zhang & Liu — UAV swarm network modeling and resilience assessment (Sensors 24(1):11) | 10.3390/s24010011 | CC BY |
| P3 | 2024 | Gaydamaka et al. — Dynamic topology organization and maintenance for autonomous UAV swarms (IEEE TMC 23(5)) | 10.1109/TMC.2023.3293034 | CC BY |
| P4 | 2025 | Huang et al. — Graph attentional based agglomerative cluster for UAV swarm networks (IEEE TNSE 12(4)) | 10.1109/TNSE.2025.3559215 | Kapalı (indirildi) |
| P5 | 2026 | Li et al. — Distributed biconnectivity-preserving flocking with fast obstacle avoidance (Complex Intell. Syst. 12(10)) | 10.1007/s40747-026-02343-y | CC BY-NC-ND |

Figür kullanımı: CC BY → atıfla; CC BY-NC-ND → değiştirmeden, atıfla; kapalı → yalnızca sınıf içi, atıfla, çevrimiçi paylaşılmaz.

## Slayt planı (16 + kaynakça/yedek)

| # | Slayt | İçerik |
| --- | --- | --- |
| 1 | Kapak | |
| 2 | Neden İHA Sürüleri? Uygulama Alanları | Endüstriyel denetim + Meshine bağlamı |
| 3 | İHA Sürü Ağı (FANET) Nedir? | G(t)=(V,E(t)); birim disk grafı (i,j)∈E(t) ⇔ ‖pᵢ(t)−pⱼ(t)‖ ≤ R |
| 4 | Neden Karmaşık Ağ? | Ders Bölüm 1'deki 4 özellik: büyük, düzensiz, dinamik, omurga |
| 5 | Ağ Mimarileri ve Topolojiler | Merkezi / merkeziyetsiz / dağıtık / küme tabanlı |
| 6 | Ağ Metrikleri | Derece, kümelenme katsayısı, ort. yol uzunluğu, arasındalık, λ₂, k-bağlantılılık |
| 7 | Kritik İHA'lar: Çalışılmış Örnek | 12 düğümlü sürü; arasındalık + kesme düğümü; bir İHA düşünce ağ bölünür |
| 8 | Araştırma Manzarası 2022–2026 | Zaman çizelgesi; 5 makale → 5 tema |
| 9–13 | Makale 1–5 | Problem · Ağ modeli · Yöntem · Veri/Deney · Bulgu · Sınırlılık · Ders bağlantısı + 1 figür |
| 14 | Veri Setleri ve Değerlendirme | Simülasyon/gerçek, araç, ölçek, tekrar üretilebilirlik |
| 15 | Karşılaştırmalı Analiz | 5 makale × 5 boyut |
| 16 | Araştırma Boşlukları → Sunum II | Çalışma yönü + aday veri |
| + | Kaynakça (IEEE) + yedek slaytlar | Süreye sayılmaz |

## Tasarım ve projeksiyon okunabilirliği

Hoca UI/UX'e dikkat ediyor; slaytlar sınıfta projeksiyonla okunur olmalı.

| Kural | Değer |
| --- | --- |
| Font | Arial (sınıf bilgisayarında kesin var; python-pptx font gömmez) |
| Boyutlar | Başlık ≥ 32 pt · gövde ≥ 22 pt · tablo ≥ 18 pt · kaynak notu 12 pt (tek istisna) |
| Kontrast | Açık zemin + koyu metin; metin kontrastı ≥ 7:1 (projektör renkleri soldurur) |
| Yoğunluk | Slayt başına tek mesaj; başlık = iddia cümlesi; ≤ 4 madde, madde ≤ 8 kelime |
| Ağ çizimleri | Düğüm ≥ 0.35 inç, kenar ≥ 2.5 pt; renk körü güvenli palet; renk + şekil birlikte kodlanır |
| Makale figürleri | İlgili panel kırpılır; içindeki yazı 18 pt eşdeğerinin altındaysa yeniden çizilir |
| Tablolar | ≤ 6 satır × 5 sütun; hücre ≤ 3 kelime |
| Formüller | matplotlib mathtext ile yüksek DPI PNG; slaytta en fazla 1–2 formül |
| Kenar boşluğu | ≥ 0.5 inç (projektör kırpması) |
| Yön bulma | Altta bölüm göstergesi + slayt numarası |
| Test | PNG render → %50 ölçekte "arka sıra" kontrolü + gri tonlama kontrolü |

## Klasör yapısı

```
0-Lessons/Complex-Networks-UAV-Swarms/   # git: kaynak + script (final proje de burada)
  PLAN.md
  notes/papers/P1..P5.md                 # makale başına kanıt çıkarımı
  notes/evidence_matrix.md               # 5 makale × 9 alan, sayfa/şekil referanslı
  deck/sunum1.yaml                       # slayt metni + kaynaklar + konuşmacı notları (tek kaynak)
  figures/make_figures.py                # NetworkX/matplotlib → PNG (+ makale figürü kırpma)
  deck/build_sunum1.py                   # python-pptx → .pptx (--drive: Drive'a kopyala)
  deck/preview.py                        # kaba PNG önizleme + metin taşması kontrolü
Drive/.../Alg4ComplexNtw/
  papers/                                # PDF'ler (git dışında, telif)
  Sunum1/                                # teslim: .pptx + .pdf
```

## Fazlar

| Faz | Tarih | Süre | Çıktı | Kontrol noktası |
| --- | --- | --- | --- | --- |
| 0 | 26 Eki | 20 dk | PLAN.md, klasör, PDF'ler | ✓ |
| 1 | 26 Eki | ~3 sa | `notes/papers/*.md` + `evidence_matrix.md` | ✓ |
| 2–3 | 26 Eki | ~3 sa | `deck/sunum1.yaml` + figürler + deste v1 (Drive: `Sunum1/`) | Kullanıcı PowerPoint'te bakar |
| 4 | 31 Eki–1 Kas | ~2 sa | Render QA, 15 dk prova, düzeltmeler | Son onay |

## Riskler

1. Süre sınırı doğrulanmadı → 15 dk ana akış + yedek slaytlar.
2. Render QA: yeni kurulum yok (karar 26 Eki). Keynote otomasyonu çalışmadı → `deck/preview.py` (Arial ölçüleriyle kaba önizleme + taşma kontrolü); son kontrolü kullanıcı PowerPoint'te yapar.
3. Figür lisansları → yukarıdaki kural.
4. Meshine verisi → Sunum 1'de yalnızca "aday veri".
5. Türkçe terim tutarlılığı → `sunum1_content.md` başında TR–EN terim sözlüğü.

## Sunum 2 (ayrı plan, 2 Kasım sonrası)

Çalışma yönü: düğüm ve bağlantı hatalarında İHA sürülerinin dayanıklı dinamik topolojisi.
Yeniden kullanılabilir varlık: `../Advanced-Networking-and-Distributed-Systems/` Project 1 — dinamik ağlarda MDS + Gauss-Markov mobilite simülasyonu.
Veri adayları: kontrollü sentetik G(t) anlık görüntüleri; Meshine telemetrisi (izin varsa).
