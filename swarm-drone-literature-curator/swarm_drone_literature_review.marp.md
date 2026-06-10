---
marp: true
theme: metropolis-ege
paginate: true
math: katex
size: 16:9
html: true
footer: "Akademik Literatür İncelemesi"
---

<!-- _class: lead -->
<!-- _paginate: false -->

# Sürü Dron Sistemleri Literatür İncelemesi
## Güncel araştırma eksenleri üzerinden değerlendirme

<div class="caption">29 Nisan 2026</div>

<!--
Bu sürüm, önceki sunumun kopyası korunarak yeniden kurulmuştur.
Yeni sürümde figürler doğrudan indirilebilen makalelerden alınmıştır.
Akış, klasik yöntemleri kısa bir arka plan olarak bırakıp 2024-2026 literatüründeki kırılma alanlarına odaklanır.
-->

---

# Sürü Zekâsı ve Gelişim Paradigması

- **Sürü zekâsı (swarm intelligence):** Kuş sürüleri, balık toplulukları ve karınca kolonileri gibi doğal sistemlerden esinlenen; basit yerel kurallarla karmaşık kolektif davranış üreten merkeziyetsiz yapıdır.
- **Beş katmanlı çerçeve:** Güncel çalışmalar karar alma, rota planlama, kontrol, iletişim ve uygulama katmanlarını birlikte ele almaktadır.
- **Simülasyon merkezli metodoloji:** Fiziksel test maliyeti ve riskleri nedeniyle literatür, PX4, Gazebo ve MATLAB tabanlı yüksek sadakatli ortamlara güçlü biçimde kaymıştır.
- **Sonuç:** Alan artık yalnızca uçuş kontrolü değil; siber-fiziksel sistem (cyber-physical system) ölçeğinde bir araştırma alanıdır.

<!--
Bu slayt, eski içerikten korunan kavramsal çerçeveyi geri getiriyor.
Bu başlangıç, güncel literatür kaymasını tartışmadan önce alanın ortak temelini kurmak açısından akademik olarak daha dengeli.
-->

---

# Sunum Çerçevesi

- Klasik çekirdek: dağıtık kontrol (distributed control), konsensüs (consensus), formasyon denetimi (formation control)
- Yeni araştırma kümeleri: etmen tabanlı yapay zekâ, federe semantik C-SLAM, ağ uyarlaması, enerji farkındalıklı otonomi ve insan-sürü etkileşimi
- Figür seçimi ilkesi: sistem mimarisi, iş akışı ve görev-ölçüm grafikleri
- Temel amaç: alanın nereye kaydığını göstermek ve açık araştırma boşluklarını görünür kılmak

<!--
İlk slaytta metodolojik çerçeveyi sabitliyorum.
Sunum teknoloji öğretmeyi değil, literatürde hangi başlıkların hızla merkezileştiğini göstermeyi hedefliyor.
Bu yüzden figürler de algoritma ayrıntısından çok mimari ve değerlendirme düzeyinde seçildi.
-->

---

# Klasik Çekirdek Artık Başlangıç Noktasıdır

- Boids, PSO, Yapay Potansiyel Alanlar (APF) ve Model Öngörülü Denetim (MPC) literatürde hâlâ referans araçlardır.
- Ancak 2024 sonrasında katkı, bu araçların tek başına iyileştirilmesinden çok daha büyük sistem mimarilerine yerleştirilmesinde üretilmektedir.
- Dolayısıyla güncel makaleler, hareket koordinasyonundan ziyade **karar paylaşımı, algı füzyonu, ağ uyarlaması ve dayanıklılık** eksenlerinde ayrışmaktadır.

> Bu nedenle doktora düzeyinde asıl soru, "hangi denetleyici?" değil; "hangi sistem bağlamında hangi denetleyici ve hangi bilgi akışı?" sorusudur.

<!--
Bu slaytta izleyiciye temel ayrımı veriyorum.
Klasik araçlar kaybolmadı; fakat yeniliğin yeri değişti.
Yeni literatür artık kontrol yasasını tek başına değil, hesap, ağ, algı ve güvenlik katmanlarıyla birlikte ele alıyor.
-->

---

# Literatürdeki Kayma

![Araştırma eksenlerindeki kayma](./assets/research_shift_map.svg)

<div class="caption">Klasik koordinasyondan sistem-düzeyi otonomiye geçişin kavramsal özeti.</div>

<!--
Eski sunumdaki kavramsal şema burada yeniden kullanılıyor.
Bu görsel, kalan tüm başlıkların neden klasik denetleyici tartışmasından çok sistem mimarilerine kaydığını açıklıyor.
-->

---

# Etmen Tabanlı Yapay Zekâ ve Uç Bilişim

- **Nguyen, Truong ve Le (2026):** Çok etmenli karar verme, bulut-uç-araç katmanları arasında bölüştürülmektedir.
- **AI-Enhanced Swarm Drones (2024):** Dağıtık görev tahsisi ile çevresel keşif aynı çerçevede ele alınmaktadır.
- Literatürdeki temel değişim, sürünün yalnızca konumsal değil, giderek **bilişsel olarak otonom** hale getirilmesidir.
- Kritik açık sorunlar: gecikme (latency), güven (trust), açıklanabilirlik (explainability) ve kaynak kısıtı.

<!--
Bu bölümde agentic AI çizgisini merkezileştiriyorum.
Yeni makalelerde mesele LLM kullanmak değil; kararın hangi kısmının araç üzerinde, hangi kısmının uç düğümde kalacağıdır.
Bu katmanlaşma, görev süresi ve otonomi kalitesini doğrudan belirliyor.
-->

---

<!-- _class: visual -->

# Etmen Tabanlı Yapay Zekâ İçin Üç Dağıtım Mimarisi

![Çok etmenli yapay zekâ dağıtım mimarileri](./assets/paper_figures/agentic_ai_meets_edge_computing/figure1_architectures.png)

<div class="caption">Bağımsız, uç destekli ve uç-bulut hibrit sürü mimarilerinin karşılaştırması.</div>
<div class="source-note">Kaynak: Nguyen, T. M., Truong, V. T. ve Le, L. B. (2026), <i>Agentic AI Meets Edge Computing in Autonomous UAV Swarms</i>, Figure 1.</div>

<!--
Bu şekil üç dağıtım stratejisini aynı anda gösterdiği için sunumun en önemli görsellerinden biri.
Literatürde otonomi seviyesi ile ağ bağımlılığı arasındaki temel dengeyi tek bakışta anlatıyor.
-->

---

<!-- _class: visual -->

# Görev-Özgül Agentic AI Sürü Mimarisi

![Yangın arama kurtarma için agentic AI sürü sistemi](./assets/paper_figures/agentic_ai_meets_edge_computing/figure2_wildfire_system.png)

<div class="caption">Yangın arama-kurtarma senaryosunda agentic AI destekli görev akışı.</div>
<div class="source-note">Kaynak: Nguyen, T. M., Truong, V. T. ve Le, L. B. (2026), <i>Agentic AI Meets Edge Computing in Autonomous UAV Swarms</i>, Figure 2.</div>

<!--
Önceki şekil genel mimariydi; bu şekil ise belirli bir görev senaryosundaki iş akışını gösteriyor.
Bu ikili kullanım, mimari argümanı soyut olmaktan çıkarıp uygulamaya bağlıyor.
-->

---

# Federe Semantik C-SLAM ve GPS-Engelli Seyrüsefer

- **D2SLAM (2024):** Dağıtık görsel-ataletsel işbirlikçi SLAM için güçlü bir altyapı sağlamaktadır.
- **FedS-SLAM (2025):** Ham veri yerine özellik paylaşımı, semantik süzme ve dinamik nesne ayrıştırma vurgusu taşımaktadır.
- Bu araştırma kümesinin ana yönü, çok araçlı haritalamayı yalnızca geometri problemi olmaktan çıkarıp **anlamsal ve ağ-farkındalıklı** hale getirmesidir.
- Açık sorun: düşük dokulu sahnelerde yeniden konumlama ve araçlar arası küresel tutarlılık.

<!--
Bu bölümde iki makaleyi birlikte okumak önemli.
D2SLAM daha güçlü bir dağıtık sistem mimarisi sunarken, FedS-SLAM semantik ve federe öğrenme yönünü öne çıkarıyor.
Birlikte okunduğunda alanın nereye kaydığı çok daha net görünüyor.
-->

---

<!-- _class: visual -->

# İki Güncel C-SLAM Mimarisi

<div class="figure-grid-2">
<div class="paper-card">

![FedS-SLAM sistem mimarisi](./assets/paper_figures/feds_slam_federated_semantic_collaborative_slam/figure1_architecture.png)

<div class="caption">FedS-SLAM: federe semantik veri akışı ve görev ayrımı.</div>
<div class="source-note">Kaynak: <i>FedS-SLAM: A Federated Semantic Collaborative SLAM System for UAV Swarms in Dynamic Environments</i> (2025), Fig. 1.</div>

</div>
<div class="paper-card">

![D2SLAM sistem mimarisi](./assets/paper_figures/d2slam_collaborative_visual_inertial_slam/figure2_architecture.png)

<div class="caption">D2SLAM: her İHA üzerinde çalışan dağıtık işbirlikçi SLAM mimarisi.</div>
<div class="source-note">Kaynak: Li vd. (2024), <i>D2SLAM</i>, Figure 2.</div>

</div>
</div>

<!--
Yan yana kullanım burada özellikle önemli.
Sol tarafta federe ve semantik eksen, sağ tarafta daha saf dağıtık SLAM mimarisi görülüyor.
İzleyiciye alanın yalnızca teknik olarak değil, mimari olarak da çoğullaştığını gösteriyor.
-->

---

<!-- _class: visual -->

# D2SLAM'de İletişim ve Harita Birleştirme

<div class="figure-grid-2">
<div class="paper-card">

![D2SLAM iletişim durum makinesi](./assets/paper_figures/d2slam_collaborative_visual_inertial_slam/figure4a_comm_state_machine.jpg)

<div class="caption">İletişim kiplerinin durum makinesi.</div>
<div class="source-note">Kaynak: Li vd. (2024), <i>D2SLAM</i>, Figure 4(a).</div>

</div>
<div class="paper-card">

![D2SLAM harita birleştirme](./assets/paper_figures/d2slam_collaborative_visual_inertial_slam/figure4b_map_merge.png)

<div class="caption">Araçlar arası harita birleştirme akışı.</div>
<div class="source-note">Kaynak: Li vd. (2024), <i>D2SLAM</i>, Figure 4(b).</div>

</div>
</div>

<!--
Bu slayt D2SLAM'in yalnızca poz kestiren bir sistem olmadığını, iletişim rejimi ve harita birleştirmeyi birlikte tasarladığını gösteriyor.
Bu, dağıtık SLAM'i sistem düzeyine taşıyan ana kırılmalardan biri.
-->

---

<!-- _class: visual -->

# Dinamik Ortam ve Ortak Optimizasyon

<div class="figure-grid-2">
<div class="paper-card">

![FedS-SLAM harita karşılaştırması](./assets/paper_figures/feds_slam_federated_semantic_collaborative_slam/figure5_map_comparison.jpg)

<div class="caption">Dinamik nesnelerin filtrelenmesiyle elde edilen daha temiz statik harita.</div>
<div class="source-note">Kaynak: <i>FedS-SLAM</i> (2025), Fig. 5.</div>

</div>
<div class="paper-card">

![D2VINS factor graph](./assets/paper_figures/d2slam_collaborative_visual_inertial_slam/figure9_factor_graph.png)

<div class="caption">D2VINS içinde kayan pencere durumlarının faktör grafı.</div>
<div class="source-note">Kaynak: Li vd. (2024), <i>D2SLAM</i>, Figure 9.</div>

</div>
</div>

<!--
Bu ikili, alanın iki farklı seviyesini birlikte veriyor.
Sol tarafta çıktı kalitesi, sağ tarafta bu çıktıyı üreten optimizasyon yapısı var.
Bu sunumsal olarak güçlü bir eşleşme çünkü hem sonuç hem mekanizma aynı slaytta okunuyor.
-->

---

# Ağ-Farkındalıklı Sürü Eşgüdümü

- **AI-Enhanced Swarm Drones (2024):** Sürü ağını ve çevresel görevleri aynı deney düzeni içinde ele almaktadır.
- **Adaptive Drone Swarm Networks (2025):** Erişim kısıtları nedeniyle PDF indirilememiş olsa da, literatür ağ rol uyarlamasını ve kip değişimini ön plana çıkarmaktadır.
- Güncel eğilim, haberleşmeyi altyapı değil doğrudan **karar ve görev performansı değişkeni** olarak ele almaktır.
- Açık sorun: bağlantı kalitesi, enerji ve görev başarımı için birleşik değerlendirme çerçevesinin eksikliği.

<!--
Bu bölümde erişilebilen figürleri AI-Enhanced çalışmasından kullanıyorum; çünkü deneysel olarak ağ ve sürü davranışını birlikte gösteriyor.
Metinsel çerçevede ise 2025 adaptif ağ literatürünü üst katman olarak bağlıyorum.
-->

---

<!-- _class: visual -->

# Sürü Ağı ve Görev Performansı

<div class="figure-grid-2">
<div class="paper-card">

![Swarm drone network](./assets/paper_figures/ai_enhanced_swarm_drones_decentralized_coordination/figure2_swarm_network.png)

<div class="caption">Algılama ve iletişim modülleriyle tanımlanan sürü ağı.</div>
<div class="source-note">Kaynak: <i>AI-Enhanced Swarm Drones: Decentralized Coordination</i> (2024), Figure 2.</div>

</div>
<div class="paper-card">

![Hybrid CRW-LF sonuçları](./assets/paper_figures/ai_enhanced_swarm_drones_decentralized_coordination/figure8_experiment2_results.png)

<div class="caption">Hibrit keşif stratejisinin hata dağılımı açısından üstünlüğü.</div>
<div class="source-note">Kaynak: <i>AI-Enhanced Swarm Drones: Decentralized Coordination</i> (2024), Figure 8.</div>

</div>
</div>

<!--
Bu slayt ağ yapısı ile ölçülebilir görev çıktısını yan yana koyuyor.
Bu yüzden yalnızca altyapı mimarisi değil, ağ-farkındalıklı performans düşüncesini de destekliyor.
-->

---

# İnsan-Sürü Etkileşimi

- **DVRP-MHSI (2025):** Çok modlu arayüzlerin aynı araştırma platformunda birleştirilmesini önermektedir.
- **CoBe XR (2025):** Operatörün sürüyü bedenlenmiş komutlar ve niyet alanları üzerinden yönlendirmesine odaklanmaktadır.
- Güncel kırılma, mikro-yönetimden **soyut davranış komutlarına** geçiştir.
- Açık sorun: bilişsel yük (cognitive load) ve denetlenebilir özerklik (supervised autonomy) arasındaki nicel denge.

<!--
İnsan-sürü etkileşimi bölümü, teknik sistemlerin kullanıcıyla nasıl bağlandığını gösteriyor.
Bu başlık giderek daha kritik çünkü yüzlerce ajanı klasik arayüzlerle yönetmek pratik olarak sürdürülemez.
-->

---

<!-- _class: visual -->

# İnsan-Sürü Etkileşimi İçin Kavramsal Çerçeve

<div class="figure-grid-2">
<div class="paper-card">

![İnsan sürü etkileşimi kavramsal şema](./assets/human_swarm_xr.svg)

<div class="caption">Niyet alanları, bedenlenmiş etkileşim ve çok modlu komut mantığı.</div>

</div>
<div class="paper-card">

![DVRP-MHSI formasyon yönlendirme](./assets/paper_figures/dvrp_mhsi_multimodal_human_swarm_interaction/figure9a_formation_guidance.png)

<div class="caption">Çok modlu insan girdisiyle formasyon yönlendirme örneği.</div>
<div class="source-note">Kaynak: <i>DVRP-MHSI</i> (2025), Fig. 9(a)-(b) bağlamından çıkarılan görsel.</div>

</div>
</div>

<!--
Önceki taşma yapan iki slayt burada tek, daha dengeli bir görsel slayta indirildi.
Soldaki kavramsal eski şema okunabilirliği koruyor; sağdaki makale figürü ise deneysel karşılığını veriyor.
-->

---

# Çapraz-Alan, Güvenlik ve Enerji: Kalan Büyük Boşluklar

- Çapraz-alan sürüleri (cross-domain swarms), farklı kinematikleri ortak görev mantığı altında birleştirmeyi gerektiriyor.
- Siber dayanıklılık (cyber resilience), artık yalnızca şifreleme değil; kimlik, güven puanı ve olay kaydı katmanlarını kapsıyor.
- Enerji farkındalıklı otonomi, görev tahsisi ve ağ kararı ile birlikte ele alınmaya başlandı; ancak ortak standart henüz yok.
- Bu üç başlıkta güçlü güncel makaleler saptandı; fakat bazı yayıncı engelleri nedeniyle tüm görseller doğrudan indirilemedi.

<!--
Bu slayt, henüz figür yerleştirmediğimiz ama teorik olarak merkezi önemde olan üç hattı bir araya getiriyor.
Sunumun açık dürüstlüğü açısından erişim kısıtını da not etmek önemliydi.
-->

---

<!-- _class: visual -->

# Çapraz-Alan ve Enerji İçin Kavramsal Şemalar

<div class="figure-grid-2">
<div class="paper-card">

![Çapraz alan koordinasyon şeması](./assets/cross_domain_matrix.svg)

<div class="caption">Heterojen platformlarda üst düzey görev mantığı ile alt düzey uygulanabilir yörünge üretiminin ayrıştırılması.</div>

</div>
<div class="paper-card">

![Enerji farkındalıklı otonomi şeması](./assets/energy_autonomy_map.svg)

<div class="caption">Batarya belirsizliği, kapsama ve enerji hasadının ortak planlama problemi haline gelişi.</div>

</div>
</div>

<!--
Bu slayt, erişemediğimiz bazı yayıncı figürlerinin yerine önceki sürümde oluşturulan temiz kavramsal şemaları geri getiriyor.
Akademik akış açısından bu iki başlık aynı sistem sorununun iki yüzü gibi okunuyor: heterojen koordinasyon ve kaynak kısıtı.
-->

---

<!-- _class: visual -->

# Dağıtık Güven ve Değerlendirme Boşluğu

<div class="figure-grid-2">
<div class="paper-card">

![Dağıtık güven mimarisi](./assets/security_stack.svg)

<div class="caption">Kimlik, hafif kriptografi, güven puanı ve olay kaydı katmanlarının bütünleşik görünümü.</div>

</div>
<div class="paper-card">

![Benchmark boşluğu](./assets/benchmark_gap.svg)

<div class="caption">Ölçülen boyutlar artarken ortak benchmark altyapısının geride kalması.</div>

</div>
</div>

<!--
Bu slayt, önceki sunumdaki iki yararlı kavramsal şemayı yeniden kullanıyor.
Solda güven mimarisi, sağda metodolojik değerlendirme boşluğu var; birlikte okunduğunda alanın hem teknik hem ölçümsel eksiklerini görünür kılıyor.
-->

---

# Değerlendirme Paradigması ve Araştırma Çıkarımları

- Yeni çalışmalar, başarı oranı yanında gecikme, yeniden konumlama, enerji, saldırı toleransı ve açıklanabilirliği birlikte ölçmektedir.
- Simülasyondan gerçeğe geçiş (sim-to-real transfer), artık ek problem değil; merkezi metodolojik problemdir.
- Türkiye için güçlü araştırma fırsatı; GNSS-bağımsız seyir, güvenli ağlar ve enerji-farkındalıklı sürü mimarilerini aynı test düzeninde birleştirmektir.
- Alanın yönü, daha fazla otonomiden çok **daha güvenilir otonomiye** doğru kaymaktadır.

<!--
Kapanış cümlesi özellikle önemli: daha otonom sistemler değil, daha güvenilir otonom sistemler dönemi başlıyor.
Bu, hem literatür okumasının hem de olası doktora tez hattının ana sonucu olarak sunulabilir.
-->

---

# Kullanılan Makale Figürleri

<div class="small">

1. Nguyen, T. M., Truong, V. T., Le, L. B. (2026). *Agentic AI Meets Edge Computing in Autonomous UAV Swarms*. Fig. 1-2.

2. *FedS-SLAM: A Federated Semantic Collaborative SLAM System for UAV Swarms in Dynamic Environments* (2025). Fig. 1, 2, 5.

3. *AI-Enhanced Swarm Drones: Decentralized Coordination* (2024). Figure 2, 8.

4. Li, X., vd. (2024). *D2SLAM: Decentralized and Distributed Collaborative Visual-Inertial SLAM System for Aerial Swarm*. Figure 2, 4(a), 4(b), 9.

5. *DVRP-MHSI: Dynamic Visualization Research Platform for Multimodal Human-Swarm Interaction* (2025). Fig. 2, 3, 9.

</div>

<!--
Bu slayt, görsel atıflarını toplu biçimde sunuyor.
Slayt içi kaynak notları ile birlikte kullanıldığında akademik izlenebilirlik korunuyor.
-->

---

# Güncel Referanslar

<div class="tiny">

[1] *Agentic AI Meets Edge Computing in Autonomous UAV Swarms*, 2026.

[2] *AI-Enhanced Swarm Drones: Decentralized Coordination*, CEUR-WS, 2024.

[3] Li, X., et al. *D2SLAM: Decentralized and Distributed Collaborative Visual-Inertial SLAM System for Aerial Swarm*, 2022-2024.

[4] *A Federated Semantic Collaborative SLAM System for UAV Swarms in Dynamic Environments*, 2025.

[5] *Development of Adaptive Drone Swarm Networks*, 2025.

[6] *Enhancing Drone Swarm Efficiency Through a High-Flexibility Biomimetic Formation Algorithm*, 2024.

[7] *Energy-Efficient Collaborative Target Tracking in AAV Swarms via Enhanced Voronoi Partitioning*, 2025.

[8] *Drone Swarm Energy Management* ve ilişkili POMDP-DDPG hattı, 2025-2026.

[9] *Distributed Self-Organizing Control for Cross-Domain Unmanned Swarm Multi-Target Tracking Under Constrained Communication*, 2025.

[10] *Research on Integrated Decision-Control Cooperative Target Assignment for Cross-Domain Unmanned Systems Based on a Bi-Level Optimization Framework*, 2025.

[11] *Secure and Decentralised Swarm Authentication Using Hardware Security Primitives*, 2026.

[12] *DVRP-MHSI: Dynamic Visualization Research Platform for Multimodal Human-Swarm Interaction*, 2025.

</div>

<!--
Kaynakça, sunumda doğrudan kullanılan figürlerin ait olduğu çekirdek makaleleri ve destekleyici güncel literatürü birlikte listeliyor.
-->
