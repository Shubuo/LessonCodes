---
marp: true
theme: metropolis-ege
paginate: true
size: 16:9
lang: tr
html: true
title: "UAV-Edge Ağlarında SDN Tabanlı Kritik Trafik Korumasının Geliştirilmesi"
author: Burak Yörük
footer: "Adv. Comp. Networks | Bütünleme | Burak Yörük"
---

<style>
section.result-slide .visual-grid {
  display: grid;
  grid-template-columns: 1.18fr 0.82fr;
  gap: 22px;
  align-items: center;
}
section.result-slide .media-frame img {
  max-height: 430px;
  object-fit: contain;
}
section.compact li {
  font-size: 0.76em;
}
.small-table table {
  font-size: 0.68em;
}
.callout {
  margin-top: 18px;
  padding: 12px 16px;
  border-left: 6px solid #2f6feb;
  background: #eef5ff;
  border-radius: 8px;
  font-size: 0.72em;
}
.term-note {
  margin-top: 10px;
  color: #526274;
  font-size: 0.58em;
  line-height: 1.35;
}
</style>

<!-- _class: lead -->

# UAV-Edge Ağlarında SDN Tabanlı Kritik Trafik Korumasının Geliştirilmesi

## Bütünleme Sunumu

Burak Yörük  
Ege Üniversitesi - Adv. Comp. Networks

<!--
Sunucu notu:
Hocam merhaba. Bu sunumda önceki final sunumundan sonra yaptığım iyileştirmeleri göstereceğim. Odak noktam, UAV-Edge ağlarında kritik trafiğin tıkanıklık altında korunması. Bu kez yalnızca önceki grafikleri tekrar göstermiyorum; ek bir deney seti, daha açıklanabilir bir ilke karşılaştırması ve kod/sonuç paketini birlikte sunuyorum.
-->

---

# Bütünleme Odağı

Hocanın istediği üç başlık doğrudan hedeflendi:

1. **Final Sunumu sonrası iyileştirme:** source-side shaping'e ek olarak switch-side priority slicing tasarlandı.
2. **Yeni sonuç:** background load sweep ile 27 yeni Mininet koşusu üretildi.
3. **Kod ve rapor:** scriptler, raw loglar, CSV/JSON, grafikler, runbook ve rapor dosyaları oluşturuldu.

<div class="term-note">* source-side shaping: arka plan trafiğinin kaynak düğümde sınırlandırılması. switch-side priority slicing: darboğaz switch çıkışında kritik akışa öncelik verilmesi. raw log: deney komutlarının ham terminal çıktısı.</div>

<!--
Sunucu notu:
Bu slaytta doğrudan bütünleme kriterlerine cevap veriyorum. İlk madde, final sunumundan sonra model tarafında yaptığım iyileştirme. İkinci madde, yeni deney sonucu. Üçüncü madde de kodların ve raporun teslim edilebilir hale getirilmesi. Burada özellikle vurgulamak istediğim şey şu: sadece metin düzenlemesi yapmadım, 27 yeni Mininet koşusu aldım ve ham logları da sakladım.
-->

---

# Final Sunumundaki Durum

<div class="visual-grid">
<div>

### Önceki deney
- UAV kaynak düğümü kritik TCP trafik gönderiyordu.
- Background UDP trafik darboğaz linki dolduruyordu.
- Baseline ve priority slicing ilkeleri karşılaştırıldı.
- Ölçümler: throughput, RTT latency, packet loss, jitter.

</div>
<div class="media-frame">
<img src="../assets/mininet-results/topology_graph.png" alt="Mininet topology">
</div>
</div>

<div class="term-note">* UAV: insansız hava aracı düğümü. TCP: güvenilir veri aktarım protokolü. UDP: bağlantısız ve agresif arka plan trafik protokolü. RTT: gidiş-dönüş gecikmesi.</div>

<!--
Sunucu notu:
Final sunumunda kullandığım temel topoloji buydu. h1 kritik UAV kaynağı gibi davranıyor, h2 edge sunucu. h3 ise arka plan yükünü üreten kaynak, h4 de bu trafiğin hedefi. İki trafik türü s1 ile s2 arasındaki ortak darboğaz linkinden geçiyor. Asıl ölçmek istediğim şey, arka plan UDP trafiği bu linki doldurduğunda kritik TCP akışının ne kadar bozulduğu.
-->

---

# Tespit Edilen Eksik

Final Sunumundaki priority yaklaşımı kritik trafiği koruyordu, ancak önemli bir modelleme zayıflığı vardı:

- Önceki yaklaşımda background trafik çoğunlukla **source tarafında** kısıtlanıyordu.
- Bu, pratik olarak faydalıydı fakat SDN/OVS tarafındaki darboğaz kuyruk yönetimini tam temsil etmiyordu.
- Bütünleme için ilke, darboğaz çıkışında uygulanacak şekilde genişletildi.

<div class="callout">Yeni katkı: source-side shaping korunurken, ayrıca switch-side priority slicing deney ilkesi eklendi.</div>

<div class="term-note">* SDN: Software-Defined Networking; ağ davranışının yazılımla yönetilmesi. OVS: Open vSwitch; Mininet içinde kullanılan programlanabilir sanal switch. Kuyruk yönetimi: paketlerin darboğaz çıkışında hangi sırayla ve ne hızla gönderileceğini belirleme.</div>

<!--
Sunucu notu:
Buradaki eksik şuydu: Önceki final sunumunda kritik trafik korunuyordu ama koruma daha çok kaynak tarafında, yani h3 üzerinde arka plan trafiğini kısmak şeklindeydi. Bu geçerli bir yaklaşım, fakat SDN anlatısı açısından biraz zayıf kalıyor. Çünkü SDN tarafında asıl göstermek istediğimiz şey, switch üzerinde akışları ayırıp kritik trafiğe öncelik verebilmek. Bu yüzden bütünleme için ikinci bir yaklaşım ekledim: switch çıkışında sınıflandırma ve önceliklendirme.
-->

---

# Yeni İlke Seti

| İlke | Açıklama | Rol |
|---|---|---|
| `baseline_fifo` | Kritik TCP ve background UDP aynı kuyrukta yarışır | Kontrol grubu |
| `source_shaping` | Background kaynak `h3` üzerinde sınırlandırılır | Final Sunumu yaklaşımı |
| `switch_priority` | `s1 -> s2` darboğaz çıkışında HTB sınıfları ve IP filtreleri uygulanır | Bütünleme iyileştirmesi |

<div class="term-note">* FIFO: First-In First-Out, paketlerin geliş sırasıyla işlendiği basit kuyruk. HTB: Hierarchical Token Bucket, Linux traffic control içinde bant genişliği sınıflandırması yapan mekanizma. IP filtreleri: kaynak IP adresine göre akışları sınıfa ayırır.</div>

<!--
Sunucu notu:
Bu tabloda üç ilkeyi aynı deney koşullarında karşılaştırıyorum. baseline_fifo, hiçbir özel önlem alınmayan durum. source_shaping, final sunumundaki yaklaşımı temsil ediyor; burada arka plan kaynakta sınırlandırılıyor. switch_priority ise bütünleme için eklediğim yeni yaklaşım. Burada s1'den s2'ye çıkan darboğaz arayüzünde HTB sınıfları kuruyorum ve h1 kaynaklı kritik akışı yüksek öncelikli sınıfa alıyorum.
-->

---

# Yeni Deney Matrisi

| Parametre | Değer |
|---|---|
| Darboğaz kapasitesi | 10 Mbps |
| Propagation delay | 20 ms |
| Queue size | 20 packet |
| Background load factor | 1x, 2x, 3x |
| İlke sayısı | 3 |
| Tekrar | 3 |
| Toplam koşu | 27 |

<div class="callout">Amaç: Trafik yükü arttığında hangi ilke kritik akışı daha kararlı tutuyor?</div>

<div class="term-note">* Background load factor: arka plan trafiğinin darboğaz kapasitesinin kaç katı hızda gönderildiği. 3x, 10 Mbps linke 30 Mbps UDP yük bindirilmesi anlamına gelir.</div>

<!--
Sunucu notu:
Bu yeni deney setinde bant genişliğini 10 Mbps sabit tuttum. Çünkü burada artık kapasite değişiminden çok tıkanıklık şiddetini görmek istiyorum. Arka plan yükünü 1x, 2x ve 3x olarak artırdım. Her ilkeyi üç tekrar ile çalıştırdım. Böylece tek bir ölçüme değil, aynı koşulda tekrarlanan ölçümlerin ortalamasına bakıyorum.
-->

---

<!-- _class: result-slide -->

# Yeni Sonuç: Throughput

<div class="visual-grid">
<div class="media-frame">
<img src="../assets/mininet-policy-sweep/results/policy_throughput_results.png" alt="Throughput policy sweep">
</div>
<div>

### Değerlendirme
- `3x` yükte baseline kritik TCP throughput: **3.551 Mbps**
- `source_shaping`: **7.370 Mbps**
- `switch_priority`: **7.613 Mbps**
- Switch-side priority, baseline'a göre **%114.39 throughput artışı** sağladı.

</div>
</div>

<div class="term-note">* Throughput: kritik TCP akışının saniyede taşıyabildiği veri miktarıdır. Burada daha yüksek değer daha iyidir.</div>

<!--
Sunucu notu:
Bu slaytta throughput sonucunu anlatıyorum. En ağır durumda, yani 3x background yükte, baseline ilkesinde kritik akış sadece 3.551 Mbps alabiliyor. Source shaping bunu 7.370 Mbps'e çıkarıyor. Switch-side priority ise 7.613 Mbps ile en yüksek değeri veriyor. Buradan çıkarımım şu: Kritik akışı darboğaz çıkışında sınıflandırmak, kaynakta kısmaya göre biraz daha iyi ve SDN mantığına daha yakın bir koruma sağlıyor.
-->

---

<!-- _class: result-slide -->

# Yeni Sonuç: Latency

<div class="visual-grid">
<div>

### Değerlendirme
- `3x` yükte baseline RTT: **108.005 ms**
- `source_shaping`: **44.084 ms**
- `switch_priority`: **24.059 ms**
- Switch-side priority, baseline'a göre **%77.72 latency reduction** verdi.

</div>
<div class="media-frame">
<img src="../assets/mininet-policy-sweep/results/policy_latency_results.png" alt="Latency policy sweep">
</div>
</div>

<div class="term-note">* Latency: paketin kaynaktan hedefe gidip yanıtının dönmesi için geçen süredir. RTT, Round Trip Time anlamına gelir. Daha düşük değer daha iyidir.</div>

<!--
Sunucu notu:
Burada gecikme sonucunu gösteriyorum. Baseline ilkesinde 3x yük altında RTT 108 ms seviyesine çıkıyor. Bu, kritik kontrol trafiği için yüksek bir değer. Source shaping ile 44 ms seviyesine düşüyor. Switch-side priority ile 24 ms seviyesine kadar düşüyor. Bu fark önemli; çünkü kritik UAV komutları veya düşük gecikmeli sensör trafiğinde sadece throughput değil, gecikmenin kararlı kalması da gerekiyor.
-->

---

<!-- _class: result-slide -->

# Yeni Sonuç: Packet Loss ve Jitter

<div class="visual-grid">
<div class="media-frame">
<img src="../assets/mininet-policy-sweep/results/policy_packet_loss_results.png" alt="Packet loss policy sweep">
</div>
<div>

### Değerlendirme
- `3x` yükte baseline packet loss: **%30.000**
- `source_shaping`: **%0.000**
- `switch_priority`: **%0.000**
- Jitter baseline'da **24.502 ms**, switch-side priority'de **0.039 ms**.

</div>
</div>

<div class="term-note">* Packet loss: gönderilen paketlerin hedefe ulaşmayan yüzdesi. Jitter: gecikme dalgalanmasıdır; gerçek zamanlı trafik için düşük olması gerekir.</div>

<!--
Sunucu notu:
Bu slayt kritik çünkü kayıp ve jitter gerçek zamanlı trafik için doğrudan kaliteyi etkiliyor. Baseline ilkesinde 3x yük altında paket kaybı yüzde 30'a çıkıyor. Bu, kritik trafik için kabul edilemez. Source shaping ve switch-side priority ikisi de kritik akışta paket kaybını sıfıra indiriyor. Jitter tarafında ise switch-side priority çok daha kararlı: 24.502 ms'den 0.039 ms'ye düşüyor.
-->

---

<!-- _class: result-slide -->

# İyileştirme Özeti

<div class="visual-grid">
<div class="media-frame">
<img src="../assets/mininet-policy-sweep/results/policy_improvement_vs_baseline.png" alt="Improvement vs baseline">
</div>
<div>

### 3x Background Load
- Throughput gain: **%114.4**
- Latency reduction: **%77.7**
- Jitter reduction: **%99.8**
- Packet loss: **%30 → %0**

</div>
</div>

<div class="term-note">* Gain/reduction değerleri baseline FIFO ilkesine göre hesaplandı. Bu slayt en ağır tıkanıklık koşulundaki göreli iyileşmeyi özetler.</div>

<!--
Sunucu notu:
Bu slayt sonuçları tek karede özetliyor. Switch-side priority ilkesinde throughput kazancı yüzde 114.4, latency azalması yüzde 77.7, jitter azalması yüzde 99.8. Paket kaybı da yüzde 30'dan sıfıra iniyor. Hocaya burada söyleyeceğim ana cümle şu: Bütünleme için eklediğim ilke, sadece throughput'u artırmadı; aynı zamanda gecikme, jitter ve paket kaybını da birlikte iyileştirdi.
-->

---

<!-- _class: small-table -->

# Sayısal Özet

| İlke | Throughput Mbps | RTT ms | Loss % | Jitter ms | Throughput gain | Latency reduction |
|---|---:|---:|---:|---:|---:|---:|
| Baseline FIFO | 3.551 | 108.005 | 30.000 | 24.502 | 0.00% | 0.00% |
| Source shaping | 7.370 | 44.084 | 0.000 | 0.116 | 107.55% | 59.18% |
| Switch-side priority | 7.613 | 24.059 | 0.000 | 0.039 | 114.39% | 77.72% |

<div class="callout">En ağır tıkanıklıkta switch-side priority hem throughput hem latency hem jitter açısından en kararlı sonucu verdi.</div>

<div class="term-note">* Bu tablo 3x background load ve 20 packet queue için üç tekrarın ortalamasıdır.</div>

<!--
Sunucu notu:
Burada sayısal tabloyu açıkça okuyabilirim. Baseline FIFO 3.551 Mbps throughput, 108 ms RTT, yüzde 30 kayıp ve 24.5 ms jitter üretiyor. Source shaping iyi bir iyileştirme sağlıyor. Ancak switch-side priority en iyi gecikme ve jitter değerlerini veriyor. Bu yüzden final sunumuna göre yeni değerlendirmem daha güçlü: sadece iki ilke değil, üç ilke ve farklı tıkanıklık seviyeleri karşılaştırıldı.
-->

---

# Kod Haritası

| Dosya | Görev |
|---|---|
| `run_mininet_uav_experiment.py` | Final Sunumundaki ana deney |
| `run_mininet_policy_sweep.py` | Yeni ilke taraması deneyi |
| `analyze_policy_sweep.py` | CSV'den tablo ve grafik üretimi |
| `README_CODE.md` | Kod açıklaması |
| `PROJECT2_MULTIPASS_RUNBOOK.md` | VM üzerinde tekrar çalıştırma adımları |

<div class="term-note">* VM: Multipass üzerinde çalışan Ubuntu sanal makine. Runbook: deneyin tekrar çalıştırılması için komut rehberi.</div>

<!--
Sunucu notu:
Bu slaytı kod kısmına geçiş için kullanacağım. run_mininet_policy_sweep.py dosyasını açıp gösterebilirim. Dosyanın başında deneyin amacı yazıyor. create_network fonksiyonu topolojiyi kuruyor, apply_source_shaping ve apply_switch_priority iki farklı iyileştirme ilkesini uyguluyor, run_trial ise tek bir ölçüm koşusunu çalıştırıp CSV satırı üretiyor.
-->

---

# Tekrar Üretilebilirlik

Yeni sonuç paketi:

- `measurements.csv`: 27 deney satırı
- `summary.json`: ilke/load bazlı özet
- `raw/`: 135 ham `iperf` / `ping` log dosyası
- `policy_comparison_table.csv`: ortalama ve iyileştirme yüzdeleri
- `policy_*.png`: sunum ve rapor grafikleri

```bash
cd /home/ubuntu/mininet-uav-exp
sudo python3 run_mininet_policy_sweep.py
```

<div class="term-note">* iperf: throughput ölçüm aracı. ping: RTT ve packet loss ölçüm aracı. CSV/JSON: sonuçların tablo ve makine-okunur özet formatları.</div>

<!--
Sunucu notu:
Bu bölümde tekrar üretilebilirliği anlatacağım. Deney sadece grafik olarak kalmadı; her koşunun ham terminal çıktısı saklandı. 27 deney satırı var ve her koşu için beş ham log dosyası tutuluyor. Bu yüzden rapordaki değerler gerektiğinde ham iperf ve ping çıktılarından kontrol edilebilir.
-->

---

# Sonuç

Final Sunumu sonrası çalışma üç yönden geliştirildi:

1. **Model iyileştirildi:** source-side shaping'e ek olarak switch-side priority slicing eklendi.
2. **Yeni deney üretildi:** background load sweep ile 27 yeni Mininet koşusu alındı.
3. **Teslim kalitesi artırıldı:** kod açıklaması, runbook, raw loglar, CSV/JSON, grafikler ve rapor kaynakları ayrı klasörde toplandı.

<div class="term-note">* Bu sonuçlar, en ağır tıkanıklık koşulunda kritik trafiğin korunabildiğini gösteren ek bütünleme kanıtıdır.</div>

<!--
Sunucu notu:
Kapanışta üç cümleyle toparlayacağım. Birincisi, model tarafında switch-side priority ilkesini ekledim. İkincisi, yeni deney olarak background load sweep yaptım ve 27 koşu aldım. Üçüncüsü, kod ve sonuçları tekrar üretilebilir şekilde paketledim. En güçlü sayısal sonuç: 3x yükte packet loss yüzde 30'dan sıfıra düştü, RTT 108 ms'den 24 ms'ye indi.
-->

---

<!-- _class: lead -->

# Teşekkürler

## Soru & Cevap

<!--
Sunucu notu:
Soru gelirse özellikle iki noktayı vurgulayacağım. Bir: source shaping önceki yaklaşımı temsil ediyor, switch-side priority ise bütünlemede eklediğim daha SDN uyumlu yaklaşımdır. İki: Bu çalışma Mininet emülasyonudur; gerçek kablosuz fiziksel ortamı birebir modellemez, fakat ağ darboğazı ve kuyruk yönetimi davranışını kontrollü biçimde test eder.
-->
