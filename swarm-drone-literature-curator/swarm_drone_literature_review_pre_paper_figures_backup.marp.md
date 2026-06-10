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
## Güncel araştırma eksenleri ve değerlendirme

<div class="caption">29 Nisan 2026</div>

<!--
Bu sürümde temel teknolojiler arka plan bilgisi olarak tutuluyor.
Sunumun merkezi, 2024-2026 döneminde literatürü yeniden şekillendiren araştırma kümeleridir.
Görseller ayrı slaytlara taşındı; böylece her yeni eğilim görsel olarak daha temiz okunabilir.
-->

---

# Sürü Zekası ve Gelişim Paradigması

- **Sürü Zekası (SI):** Doğadaki sürü ve koloni davranışlarından (kuş, balık, karınca) ilham alan; basit yerel kurallarla etkileşime girerek en karmaşık küresel problemleri çözebilen merkeziyetsiz bir yapıdır.
- **Beş Katmanlı Hiyerarşi:** Sürü zekası sistemleri; her bir etmenin etkileşimini ve sistem bütünselliğini güvence altına almak amacıyla karar alma, rota planlama, kontrol, iletişim ve uygulama olmak üzere beş temel katmanda sınıflandırılmaktadır.
- **Simülasyon Odaklı Metodoloji:** Fiziksel testlerin getirdiği yüksek maliyet ve riskler nedeniyle; araştırmalar gerçek dünya fizik kurallarını yansıtan yüksek sadakatli sanal ortamlara (PX4, Gazebo, MATLAB) kaymış ve bu durum arama-kurtarmadan tarıma kadar geniş bir yelpazede strateji üretimine olanak tanımıştır.
 
<!--
-->

---

# Literatürdeki Değişim

- Güncel çalışmalarda Dağıtık kontrol (distributed control), konsensüs (consensus) ve formasyon denetimi (formation control) temel omurgayı oluşturmaktadır.
- Boids, PSO (Parçacık Sürüsü Optimizasyonu), Yapay Potansiyel Alanlar (APF) ve Model Öngörülü Kontrol (MPC) artık çoğu makalede başlangıç arka planı olarak ele alınmaktadır.
- Güncel katkı, bu araçların hangi **yeni sistem bağlamları** içinde yeniden yorumlandığıdır.
- 2024 sonrasında literatür, tekil algoritmadan çok **sistem-düzeyi otonomi** yönüne kaymıştır.

<!--
Bu slaytta temel ayrımı kuruyorum.
Alan artık daha iyi bir klasik denetleyici bulma yarışından ibaret değil.
Yeni değer, bu klasik araçların uç bilişim, federe algılama, enerji planlama ve siber güvenlik gibi daha büyük mimarilere nasıl yerleştirildiğinde ortaya çıkıyor.
-->

---

<!-- _class: visual -->

# Araştırma Eksenlerindeki Kayma

![Araştırma eksenlerindeki kayma](./assets/research_shift_map.svg)

<div class="caption">Klasik koordinasyondan sistem-düzeyi otonomiye geçişin kavramsal özeti.</div>

<!--
Bu görsel, alanın neden yeniden çerçevelenmesi gerektiğini tek bakışta gösterir.
Sol taraf klasik çekirdeği, sağ taraf ise güncel araştırma sınırlarını temsil ediyor.
Benim temel argümanım, doktora düzeyinde asıl katkının artık sağ taraftaki kümelerde üretildiğidir.
-->

---

# Etmen Tabanlı Yapay Zekâ ve Uç Bilişim

- **2026 | Agentic AI Meets Edge Computing in Autonomous UAV Swarms:** Karar üretimini bulut, uç ve araç üstü katmanlara ayırmaktadır.
- **2024 | AI-Enhanced Swarm Drones: Decentralized Coordination:** Dağıtık görev tahsisini yapay zekâ ile bütünleştirmektedir.
- Yeni yönelim, sürünün yalnızca hareket eden değil, **yorumlayan ve önceliklendiren** bir yapıya dönüşmesidir.
- Açık sorun: gecikme (latency), güven (trust) ve açıklanabilirlik (explainability) aynı çerçevede yeterince çözülememektedir.

<!--
Önceki nesil sürü literatüründe karar verme daha sığdı.
Yeni çalışmalar, kararın hangi katmanda üretileceğini, hangi kısmının araç üzerinde kalacağını ve hangi kısmının uç düğüme taşınacağını tartışıyor.
Bu değişim, sürü sistemlerini bilişsel olarak daha özerk hale getiriyor.
-->

---

<!-- _class: visual -->

# Etmen Tabanlı Yapay Zekâ Mimarisi

![Etmen tabanlı yapay zeka ve uç bilişim](./assets/agentic_edge_swarm.svg)

<div class="caption">Karar üretiminin bulut, uç ve araç üstü katmanlar arasında dağıtılması.</div>

<!--
Bu şema, güncel literatürde neden tek işlemci mantığının terk edildiğini anlatıyor.
Karar kalitesi, gecikme ve görev esnekliği artık doğrudan katmanlar arası iş bölümüne bağlı.
-->

---

# Federe Semantik C-SLAM ve GPS-Engelli Seyrüsefer

- **2022-2024 | D2SLAM:** Dağıtık görsel-ataletsel işbirlikçi SLAM için güçlü bir temel sunmaktadır.
- **2025 | Federated Semantic Collaborative SLAM:** Ham veri yerine özellik paylaşımıyla ağ yükünü azaltmaktadır.
- Yeni katkı, semantik algılama (semantic perception), hareketli nesne ayrıştırma ve araçlar arası yeniden konumlamayı aynı döngüde birleştirmesidir.
- Açık sorun: düşük dokulu ortamlarda araçlar arası tutarlılığın korunmasıdır.

<!--
Bu başlıkta asıl yenilik, konum tahmini ile anlamsal çevre yorumunun birleşmesidir.
Sistem yalnızca nerede olduğunu bilmeye çalışmıyor; hangi özelliklerin güvenilir ve paylaşılabilir olduğunu da seçiyor.
Bu yüzden federe yaklaşım yakın dönemin en güçlü araştırma hatlarından biri haline geldi.
-->

---

<!-- _class: visual -->

# Federe Semantik C-SLAM İş Akışı

![Federe semantik C-SLAM](./assets/federated_slam_pipeline.svg)

<div class="caption">Algılama, anlamsal süzme, özellik paylaşımı ve ortak harita üretiminin birleşik akışı.</div>

<!--
Görselde özellikle iki nokta önemli: ham veri paylaşılmıyor ve hareketli nesneler harita güvenilirliğini bozmadan ayrıştırılıyor.
Bu, hem bant genişliği hem de harita kalitesi açısından güncel literatürün temel kırılmasıdır.
-->

---

# Uyarlanabilir FANET ve Çift Modlu Haberleşme

- **2025 | AeroSyn benzeri mimariler:** Altyapı destekli ve altyapısız iletişim kipleri arasında geçiş önermektedir.
- **2025 | Adaptive Drone Swarm Networks:** Ağ rol dağılımını dinamikleştirerek tıkanıklığı azaltmayı hedeflemektedir.
- Yeni vurgu, kip değiştiren haberleşme (mode-switching communication), hafif veri şeması ve röle mantığıdır.
- Açık sorun: görev sürekliliğini korurken ağ yükünü ve enerji maliyetini sınırlamaktır.

<!--
Bu alan artık yalnızca paket iletimi problemi olarak görülmüyor.
İletişim mimarisi doğrudan sürü denetiminin ve güvenliğin belirleyicisi haline gelmiş durumda.
Bu yüzden ağ tasarımı, güncel sürü literatüründe bağımsız bir araştırma omurgası oldu.
-->

---

<!-- _class: visual -->

# Uyarlanabilir FANET Şeması

![Uyarlanabilir FANET ve çift modlu haberleşme](./assets/dual_mode_fanet.svg)

<div class="caption">Altyapı destekli örgü iletişim ile lider-röle yedek kipinin karşılaştırılması.</div>

<!--
Bu görsel, ağın neden statik değil bağlama duyarlı kurulması gerektiğini gösteriyor.
Özellikle büyük sürülerde kip değiştirme, görev bütünlüğünü koruyan ana mekanizmalardan biri olarak öne çıkıyor.
-->

---

# Biyolojik Esinli Yöntemlerin Yeni Biçimleri

- **2024 | Boids + DRL hibritleri:** Klasik yerel kuralları öğrenme tabanlı uyarlama ile birleştirmektedir.
- **2024 | Esnek biomimetic formasyon algoritmaları:** Formasyon sertliğini azaltıp çevresel uyumu artırmaktadır.
- **2025-2026 | Stigmerjik kaçınma ve ayarlanabilir gürültü (tunable noise):** Sürü sıkışmasını azaltmak için kontrollü rastlantısallık kullanmaktadır.
- Yeni sonuç: biyolojik esin (bio-inspiration), sabit kuraldan çok **uyarlanabilir davranış üretimi** çerçevesine dönüşmektedir.

<!--
Boids gibi klasik yaklaşımlar kaybolmadı; fakat artık öğrenme, gürültü ayarı ve dolaylı etkileşim mekanizmalarıyla birlikte yeniden okunuyor.
Bu da biyolojik esini yeniden güncel ve araştırma değeri yüksek bir alan haline getiriyor.
-->

---

<!-- _class: visual -->

# Biyolojik Esinli Hibrit Davranış

![Biyolojik esinli hibrit sürü davranışı](./assets/biohybrid_formation.svg)

<div class="caption">Düzenli akış, yerel etkileşim havzası ve uyarlanabilir kaçış davranışının birlikte gösterimi.</div>

<!--
Bu görselin amacı, biyolojik esinli yöntemlerin artık sadece estetik sürü efekti üretmediğini göstermektir.
Yeni çalışmalar, sıkışma ve çıkış problemlerini çözmek için bu mekanizmaları kontrollü biçimde yeniden tasarlıyor.
-->

---

# Enerji-Farkındalıklı Otonomi

- **2025 | POMDP-DDPG tabanlı enerji yönetimi:** Belirsiz batarya durumunda karar almayı modellemektedir.
- **2025 | Enhanced Voronoi target tracking:** Kapsama ile enerji tüketimini birlikte ele almaktadır.
- **2025-2026 | Enerji hasadı (energy harvesting):** Donanım ve görev planlama birlikte düşünülmeye başlanmıştır.
- Açık sorun: hareket, algılama ve iletişim maliyetlerini tek enerji modeli içinde birleştirecek ortak çerçevenin eksikliğidir.

<!--
Enerji artık sadece pil ömrü değil, görev sürekliliği problemi olarak ele alınıyor.
Bu yüzden yeni çalışmalar enerji planlamasını karar teorisi, kapsama ve görev tahsisi ile birleştiriyor.
-->

---

<!-- _class: visual -->

# Enerji-Farkındalıklı Otonomi Haritası

![Enerji farkındalıklı otonomi](./assets/energy_autonomy_map.svg)

<div class="caption">Batarya belirsizliği, kapsama bölümlendirmesi ve enerji hasadı eksenlerinin birlikte değerlendirilmesi.</div>

<!--
Bu görsel, enerji meselesinin tek değişkenli olmadığını anlatıyor.
Batarya, kapsama ve görev kararı aynı sistem problemi haline gelmiş durumda.
-->

---

# Çapraz-Alan Sürüleri ve Matriks Operasyonları

- **2025 | Bi-level optimization for UAV-USV-UGV coordination:** Heterojen platformlarda üst ve alt düzey karar katmanlarını ayırmaktadır.
- **2025 | Cross-domain tracking under constrained communication:** İletişim kısıtını doğrudan görev başarımına bağlamaktadır.
- Yeni vurgu, uzay-hava-kara-deniz-siber katmanlarını ortak görev mantığı içinde ele alan matriks operasyonlarıdır.
- Açık sorun: farklı kinematikleri tek bir denetim ve değerlendirme dilinde birleştirmektir.

<!--
Bu alan, sürü literatürünün hava aracı merkezinden çıkıp heterojen platformlara genişlediğini gösteriyor.
Çapraz-alan sürüleri, önümüzdeki yılların en kritik büyüme alanlarından biri olacaktır.
-->

---

<!-- _class: visual -->

# Çapraz-Alan Koordinasyon Şeması

![Çapraz alan sürüleri ve matriks operasyonları](./assets/cross_domain_matrix.svg)

<div class="caption">Üst düzey görev mantığı ile alt düzey uygulanabilir yörünge üretiminin ayrıştırılması.</div>

<!--
Bu şema heterojen sürülerde neden katmanlı optimizasyon gerektiğini netleştiriyor.
Platformlar farklı olduğu için tek aşamalı bir kontrol dili çoğu durumda yeterli olmuyor.
-->

---

# Siber Dayanıklılık ve Dağıtık Güven

- **2024-2025 | Hafif şifreleme (lightweight cryptography):** Düşük kaynaklı sürü ağlarında öne çıkmaktadır.
- **2026 | PUF tabanlı doğrulama:** Donanım kökenli kimlik güvencesi üretmektedir.
- **2024-2026 | Blockchain ve itibar katmanları:** Byzantine ajanların etkisini sınırlamaya yönelmektedir.
- Açık sorun: güvenlik kazancı ile gecikme ve enerji maliyeti arasındaki dengenin kırılgan kalmasıdır.

<!--
Güvenlik artık şifreleme seçimiyle sınırlı bir konu değil.
Kimlik, güven, kayıt ve saldırı sonrası dayanıklılık birlikte düşünülüyor.
Bu dönüşüm, sürü ağlarında güven mimarisini yeni bir araştırma alanı haline getirdi.
-->

---

<!-- _class: visual -->

# Dağıtık Güven Mimarisi

![Siber dayanıklılık ve dağıtık güven](./assets/security_stack.svg)

<div class="caption">Kimlik, hafif kriptografi, güven puanı ve olay kaydı katmanlarının bütünleşik görünümü.</div>

<!--
Görsel, güvenliğin neden çok katmanlı ele alınması gerektiğini gösteriyor.
Fakat her yeni güven katmanı aynı zamanda yeni bir gecikme ve enerji maliyeti de getiriyor.
-->

---

# İnsan-Sürü Etkileşimi 

- **2025 | CoBe XR:** Mekânsal artırılmış gerçeklik (spatial augmented reality) ile bedenlenmiş komut önermektedir.
- **2025 | DVRP-MHSI:** Göz takibi, EMG, BCI ve çoklu arayüzleri tek araştırma platformunda birleştirmektedir.
- Yeni eğilim: operatör, sürüyü tek tek araçlarla değil **niyet alanları** üzerinden yönlendirmektedir.
- Açık sorun: bilişsel yük (cognitive load) ile denetlenebilir özerklik (supervised autonomy) arasındaki ilişkinin ölçülebilir olmamasıdır.


<!--
Sürü büyüdükçe klasik kontrol arayüzleri ölçeklenmiyor.
Bu nedenle XR ve çok modlu insan-sürü etkileşimi artık ikincil bir kullanıcı deneyimi konusu değil, doğrudan görev başarımı konusu haline gelmiş durumda.
-->


<!-- _class: visual 

# İnsan-Sürü Etkileşimi Görseli

![İnsan sürü etkileşimi](./assets/human_swarm_xr.svg)

<div class="caption">Mikro-yönetim yerine niyet biçimlendirme ve çok modlu komut yaklaşımı.</div>


Bu görsel, insan operatörün sürüyü tek tek araçlar yerine davranış alanı üzerinden şekillendirdiği yeni yaklaşımı anlatıyor.
Bu, özellikle büyük sürüler için kritik bir arayüz dönüşümüdür.
-->

---

# Değerlendirme Paradigması Değişimi

- Yeni çalışmalar, başarı oranı (success rate) yanında gecikme, enerji, saldırı toleransı ve açıklanabilirliği birlikte ölçmektedir.
- Simülasyondan gerçeğe geçiş (sim-to-real transfer), artık temel metodolojik sorunlardan biridir.
- Ortak kıyaslama takımları (benchmark suites) ve standart veri kümeleri hâlâ sınırlıdır.
- Öğrenen sürüler için biçimsel doğrulama (formal verification) hâlâ en zayıf halkalardan biridir.

<!--
Bu slayt alanın nasıl değerlendirildiğinin değiştiğini özetliyor.
Artık tek ölçüt görev başarısı değil; güvenilirlik ve yeniden üretilebilirlik eşit derecede önemli.
-->

---

<!-- _class: visual -->

# Değerlendirme ve Benchmark Boşluğu

![Değerlendirme ve kıyaslama boşluğu](./assets/benchmark_gap.svg)

<div class="caption">Ölçülen boyutlar artarken ortak benchmark altyapısının hâlâ geride kalması.</div>

<!--
Görseldeki boşluk, alanın metodolojik sorununun özeti olarak okunabilir.
Literatür daha çok şey ölçüyor ama bunları ortak bir zeminde kıyaslamak hâlâ zor.
-->

---

# Türkiye İçin Araştırma Çıkarımları

- GNSS-bağımsız seyir (GNSS-independent navigation), sürü dayanıklılığı ve güvenli ağlar birlikte ele alınmalıdır.
- Uç bilişim, karşı-sürü savunması (counter-swarm defense) ve çapraz-alan entegrasyon aynı araştırma paketinde düşünülmelidir.
- Akademik fırsat, enerji, ağ ve güvenliği aynı deney düzeneğinde birleştiren test altyapıları kurmaktır.
- Stratejik çıkarım: alanın yönü daha fazla otonomi değil, **daha güvenilir otonomi** yönündedir.

<!--
Sunumun yerel bağlamdaki sonucu şudur: Türkiye için en değerli katkı alanı, sadece platform üretmek değil; güvenilir sürü davranışı için deneysel ve kuramsal altyapı kurmaktır.
Bu, akademi ve savunma uygulaması arasındaki en doğal ortak zemindir.
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
Kaynaklar özellikle 2024-2026 kümelenmesini görünür kılacak biçimde korunmuştur.
Sunumdaki tüm ana başlıklar bu güncel literatür çizgisinden türetilmiştir.
-->
