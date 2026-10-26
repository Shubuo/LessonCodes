# Kanıt Matrisi — Sunum 1

Kaynak: `notes/papers/P1..P5.md` (her iddia orada sayfa/şekil referanslı). Sayfa = PDF sayfası.
İşaretler: **(şekil)** = değer şekilden gözle okundu, yaklaşık · **(sayım)** = tablodan bizim saydığımız · **[Yorum]** = bizim çıkarımımız.
Doğrulama: her makalenin anahtar sayıları çıkarılmış metne karşı tek tek kontrol edildi (P1 s. 3/24, P2 Tablo 3–4, P3 "3–5 kat" ve GitHub, P4 487/269 ve %80.04, P5 Menger/DBAP/1200 deneme).

## 1. Ana matris

| Alan | P1 Alam 2022 (derleme) | P2 Zhang & Liu 2024 | P3 Gaydamaka 2024 | P4 Huang 2025 | P5 Li 2026 |
| --- | --- | --- | --- | --- | --- |
| **Problem** | FANET topoloji kontrol algoritmalarını sınıflamak | Saldırı + toparlanma sürecini ölçen dayanıklılık | GPS'siz sürüde topolojiyi kurup korumak | Hareketli sürüde dengeli, dağıtık kümeleme | Engelli ortamda sürüyü 2-bağlı tutmak |
| **Ağ modeli** | G(t)=(U,E), kenar ⇔ d_ij(t) ≤ R (s. 10) | İki katmanlı (iletişim + yapısal), statik başlangıç (s. 3–4) | G=(V,A), menzil içi kenar, 1-/2-sekme bilgisi (s. 5–6) | G_t=(V_t,E_t), kenar ağırlığı α_ij öğrenilir (s. 3, 5) | G(t)=(U,E(t)), kenar ⇔ d_ij ≤ R_com=11,5 m (s. 8) |
| **Yöntem** | Taksonomi: merkezi / dağıtık / hibrit / hiyerarşik × matematiksel model (Şekil 9) | R(t) = ⟨k⟩, C, E'nin ağırlıklı min-max bileşimi (Denk. 17) | Ceza fonksiyonu en küçükleme ile 3B sanal koordinat (Alg. 1) + birleşme (Alg. 2–4) | GAT benzerliği + aşağıdan yukarı birleştirme (α>η) + oyun kuramlı CH seçimi | Yerel indüklenmiş alt graf + Menger/max-flow ile kritik komşu (Teorem 1) |
| **Deney / veri** | Kendi deneyi yok; incelenen 28 algoritmanın çoğu MATLAB/OMNeT++ (s. 35–37) | NetworkX; 55 İHA, 110 düğüm, 329 kenar; küme/rastgele/BA; 30 koşu (s. 13–15) | N=50 (30–100), R=30/50 m, %1–30 uzaklık hatası; sentetik (Tablo I) | n=200–1000, 500×500×150 m, 3B rastgele yürüyüş; sentetik (s. 11) | m=5–25, 200 m alan, statik engeller; Python+PyTorch; hücre başına 200 deneme (s. 23–26) |
| **Metrikler** | Nitel ✓/× (16 ölçüt); bağlantı oranı, λ₂ (s. 24, 35–36) | ⟨k⟩, C, E, ort. yol uzunluğu, R(t) (s. 7–10) | Topoloji benzerliği K (Pearson), yönlendirme metriği ρ (s. 10–11) | Modülerlik Q, siluet, ağ ömrü FND/LND (s. 11–12) | Görev başarısı, süre, yol kalitesi, λ₂(t), düğüm başı mesaj (s. 26–36) |
| **Ana bulgu** | 28 algoritmanın 10'u arıza toleranslı (sayım; s. 35–36) | Dereceye göre hedefli saldırıda BA en hızlı çöker (s. 16) | %30 uzaklık hatasında bile benzerlik > %90; kademeli yönteme göre 3–5 kat iyi (s. 11) | Q ≈ 0,74 (SC ≈ 0,55, AC ≈ 0,61); ilk ölüm 487 tur (en iyi rakip 269) (s. 13–15) | m=15'te 1200 denemenin 4'ünde 2-bağlılık kaybı; ≈5 mesaj/düğüm (DBAP 15–30) (s. 26–27) |
| **Sınırlılık** | Nitel karşılaştırma; tarama protokolü yok; arıza toleransı tanımsız | Ağırlıklar, menzil, hareket yok; bağlantı arızası yok; tablo–şekil çelişkileri | Arıza modeli geçici, rastgele, tek düğüm; ayrılma algoritması yok | Menzil/kenar kuralı yok; "dayanıklılık" yalnız hareketliliğe karşı | Arıza enjeksiyonu yok; ideal, senkron iletişim; yalnız koruma, onarım yok |
| **Kod / veri** | — | Veri talep üzerine; kod yok | **Kod açık:** github.com/gaydamanya/GAR (s. 15) | Yok | Yok |
| **Figür (lisans)** | Şekil 9 taksonomi → yeniden çiz (kapalı) | Şekil 1 iki katmanlı model → olduğu gibi (CC BY) | Şekil 1 üst panel → kırp; Şekil 4a → yeniden çiz (CC BY) | Şekil 3 dendrogram → olduğu gibi (IEEE, sınıf içi) | Şekil 3 indüklenmiş alt graf → olduğu gibi, kırpmadan (CC BY-NC-ND) |

## 2. Ders kavramı × makale

✓ = yöntemin çekirdeği / açıkça kullanılıyor · ~ = dolaylı ya da yalnız tanım düzeyinde · – = yok

| Ders kavramı | P1 | P2 | P3 | P4 | P5 |
| --- | --- | --- | --- | --- | --- |
| Dinamik graf G(t) | ✓ | ~ silme/ekleme | ✓ | ✓ | ✓ |
| Menzil kuralı (birim disk grafı) | ✓ terim yok | ~ ima | ✓ terim yok | – menzil yok | ✓ terim yok |
| Derece / derece dağılımı | ✓ derece | ✓ dağılım | ~ \|S_k\| | ~ k_i | ~ karmaşıklıkta |
| Kümelenme katsayısı | – | ✓ | – | – | – |
| Ort. yol uzunluğu / verimlilik | – | ✓ | ~ en kısa yol | – | – |
| Merkezilik | ~ PageRank | ✓ derece (saldırı) | ~ örtük | – | – |
| Bağlı bileşen / bölünme | ✓ | ~ izole düğüm | ✓ sürü = bileşen | – | ✓ |
| Kesme düğümü / 2-bağlılık | ~ CDSTC-JO | – | – | – | ✓ çekirdek |
| Cebirsel bağlılık λ₂ | ✓ | – | – | – | ✓ |
| Graf tabanlı kümeleme | ~ CH taksonomisi | – | – | ✓ çekirdek | – |
| Baskın küme / omurga | ✓ CDS | – | – | ~ CH omurga | – |
| Çok katmanlı ağ | – | ✓ | – | – | – |
| Hedefli arıza deneyi | – | ✓ derece | – | – | – |

**Okuma:** Hiçbir makale hareketten doğan G(t) + kritik düğüme hedefli arıza (kesme düğümü / arasındalık) + bağlılık ölçüsü (λ₂, en büyük bileşen) + onarımı birlikte ele almıyor.

## 3. Veri setleri ve değerlendirme (slayt 14)

| | Veri türü | Araç | Ölçek | Hareket | Arıza modeli | Tekrar |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | — (derleme) | MATLAB / OMNeT++ yaygın | — | RWP, RPGM, Boids… (19/28 belirtmemiş, sayım) | İkili "arıza toleransı" sütunu | — |
| P2 | Sentetik | NetworkX | 55 İHA | Yok | Rastgele + dereceye göre hedefli düğüm silme; SIR yayılımı | 30 koşu |
| P3 | Sentetik | Belirtilmemiş + GitHub kodu | 30–100 İHA | Rastgele yön modeli | Geçici tek düğüm; paket kaybı 0,05/0,1 | Belirtilmemiş |
| P4 | Sentetik | Belirtilmemiş | 200–1000 İHA | 3B rastgele yürüyüş | Yalnız enerji tükenmesi | "Birkaç" |
| P5 | Sentetik | Python + PyTorch | 5–25 İHA | 2B kinematik, lider hedefe | Yok (yalnız mesafe kaynaklı kopma) | 200 / hücre |

**Ortak sonuç:** Beş çalışmanın hiçbiri gerçek uçuş verisi ya da açık etiketli veri seti kullanmıyor; yalnız P3 kodunu yayımlamış. Sunum 2'de veri kararı (sentetik / açık kod / Meshine telemetrisi) bu yüzden ayrı bir tasarım sorusu.

## 4. Karşılaştırma tablosu taslağı (slayt 15, hücre ≤ 3 kelime)

| | Graf modeli | Odak kavram | Arıza modeli | Ölçek | Kod |
| --- | --- | --- | --- | --- | --- |
| P1 | G(t), d ≤ R | λ₂, CDS | İkili sütun | Derleme | — |
| P2 | İki katmanlı | ⟨k⟩, C, E | Hedefli düğüm | 55 İHA | Talep üzerine |
| P3 | G(t), menzil | Komşuluk, bileşen | Geçici, tek | 50 İHA | ✓ |
| P4 | G_t, ağırlıklı | Kümeleme, Q | Enerji tükenmesi | 200–1000 | — |
| P5 | G(t), R_com | 2-bağlılık | Yok | 5–25 İHA | — |

## 5. Ortak boşluklar → Sunum II (slayt 16)

1. **Arıza testi zayıf:** P4 ve P5'te düğüm/bağlantı arızası yok; P3'te yalnız geçici ve rastgele; P1'de 28 algoritmanın 18'i arıza toleranslı değil ya da belirtilmemiş (sayım).
2. **Kritik düğüm ölçülmüyor:** Kesme düğümü / arasındalık ile hedefli saldırı hiçbir makalede yok; P2 yalnız dereceyi kullanıyor.
3. **Koruma var, onarım yok:** P5 2-bağlılığı yalnız korur; arızadan sonra yeniden 2-bağlı olma mekanizması ve süresi yok.
4. **Hareket ile dayanıklılık ayrı ele alınıyor:** P2 dayanıklılığı ölçer ama hareket yok; P3–P5 hareket var ama dayanıklılık ölçümü yok.
5. **Tekrar üretilebilirlik:** Tek açık kod P3; gerçek veri yok.

**Çalışma sorusu (taslak):** Hareketli bir İHA sürüsünde kritik düğümlere (kesme düğümü, yüksek arasındalık) yönelik hedefli arızalar, rastgele arızalara göre bağlılığı (λ₂, en büyük bileşen) ne kadar daha hızlı bozar ve yerel bir onarım kuralı ağı ne kadar sürede yeniden 2-bağlı yapar?

## 6. Slayta konabilir doğrulanmış sayılar

| Makale | Sayı | Kaynak |
| --- | --- | --- |
| P1 | 28 algoritma; 10'u arıza toleranslı; mimari: 2 merkezi, 15 dağıtık, 2 hibrit, 9 hiyerarşik (sayım) | s. 34–36 |
| P1 | λ₂(L) > 0 ⇔ graf bağlı; L = D − A | s. 24 |
| P2 | 55 İHA → 110 düğüm, 329 kenar | s. 13, 15 |
| P2 | γ = 0,05 → 0,20: küme ağında min 0,0153 → 0,2002, max 0,9728 → 0,8089 | s. 18, Tablo 4 |
| P3 | N = 50; uzaklık hatası %1 ve %30; benzerlik > %90; 3–5 kat iyileşme | s. 10–11 |
| P4 | Q ≈ 0,74 / 0,61 / 0,55 (GAAC / AC / SC); FND 487'ye karşı 269 tur | s. 13–15 |
| P5 | m = 15: 1200 denemenin 4'ünde 2-bağlılık kaybı; ≈ 5 mesaj (0,1 KB) / düğüm, DBAP 15–30 (0,2–0,5 KB) | s. 26–27 |

## 7. Kullanılmayacak ya da dikkatle kullanılacak bilgiler

| Makale | Sorun | Karar |
| --- | --- | --- |
| P1 | "UDG" = Undirected Graph, birim disk grafı değil (s. 3) | Birim disk grafını kendi çerçevemiz olarak sun |
| P2 | Tablo 3'te aynı N/E için farklı ortalama dereceler; hedefli kurtarma nihai R değerleri yalnız şekilden | Tablo 3 derecelerini ve şekil okumalarını slayta koyma |
| P3 | Birleşme sonrası toparlanma: 10 adım / 20–50 adım / "birkaç saniye" | Süre verme |
| P4 | Özetteki "%80,04" türetilemiyor; γ metinde 0,4, tabloda 0,2; LEACH/ECAGT değerleri şekiller arası çelişkili | Yalnız 487 / 269 karşılaştırmasını kullan |
| P5 | Karmaşıklık iddiaları birbiriyle çelişiyor (s. 14 vs s. 22); Şekil 20'deki λ₂ belirsiz | Karmaşıklık ve Şekil 20'yi kullanma |

## 8. Figür kararları

| Slayt | Figür | İşlem | Lisans notu |
| --- | --- | --- | --- |
| 5 Mimariler | Kendi çizimimiz (P1 taksonomisi + DII infografiği ilhamı) | Çiz | Kaynak gösterilir |
| 7 Kritik İHA | `figures/out/critical_uav_example.png` | Hazır | Kendi |
| 8 Manzara | Zaman çizelgesi | Çiz | Kendi |
| 9 P1 | Şekil 9 taksonomi ya da arıza toleransı çubuk grafiği (sayım) | Yeniden çiz | Kapalı → atıf |
| 10 P2 | Şekil 1 iki katmanlı model | Olduğu gibi | CC BY |
| 11 P3 | Şekil 1 üst panel (kırp) ya da Şekil 4a (yeniden çiz, "şekilden okunmuştur") | Faz 2'de seç | CC BY |
| 12 P4 | Şekil 3 dendrogram | Olduğu gibi | © IEEE, sınıf içi |
| 13 P5 | Şekil 3 indüklenmiş alt graf | Olduğu gibi, kırpmadan | CC BY-NC-ND |
| 14–15 | Tablolar | Kendi | — |
