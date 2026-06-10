---
marp: true
theme: metropolis-ege
paginate: true
size: 16:9
header: 618 Derin Öğrenme | Kavramsal Sunum
footer: Burak YÖRÜK | Pragmatik Vurgu Tespiti
---

<!-- _class: lead -->

# Türkçe Pragmatik Vurgu Tespiti
## Teknik Ayrıntılardan Çok Problem, Anlam ve Vizyon

Bilgisayar Bilimleri sınıfı için kavramsal sunum  
Burak YÖRÜK  
Ege Üniversitesi

<!--
Speaker Notes:
Merhaba. Bu sunumda teknik metriklerden çok, çözmeye çalıştığımız araştırma problemini anlatacağım.
Ana soru şu: İnsan konuşmasındaki vurgu ve niyet, yazıya geçtiğinde kayboluyorsa, bir dil modeli bunu yeniden anlayabilir mi?
Bu soruyu özellikle Türkçe için ele alıyoruz. Çünkü Türkçe, yapısı gereği bu problem için hem zor hem de araştırma açısından çok değerli bir dil.
-->

---

# Problem ve Motivasyon

- Yazılı Türkçe, sözlü prosodiyi(konuşma ezgisi) doğrudan taşımaz.
- Pragmatik vurgu; **TTS**, **duygu analizi** ve **sohbet sistemleri** için kritiktir.
- Türkçede:
  - sözcük sırası esnek,
  - morfoloji zengin,
  - vurgu kural tabanlı olarak güvenilir modellenemez.
- Bu yüzden, **token-level deep learning** ile problemin ele alınması gerekir.

**Basit örnek:**

- “**Ben** yarın geleceğim.”
- “Ben **yarın** geleceğim.”

Bu iki cümle sözcük olarak benzer görünür, ama iletişimsel odak farklıdır.

![w:650](assets/problem-motivation.png)

<!--
Visual Idea:
Solda konuşan bir insan ve ses dalgası, sağda düz yazılmış cümle.
Alt tarafta aynı cümlenin iki vurgu varyantı ve altında “kim?” / “ne zaman?” anlam farkı.

Speaker Notes:
Bu slaytta asıl motivasyonu çok net kurmak istiyorum.
Konuşmada insanlar vurgu ve niyeti tonlama üzerinden kolayca anlıyor.
Ama yazıya geçtiğimizde bu bilgi büyük ölçüde kayboluyor.
Türkçe için problem daha da zor, çünkü sözcük sırası esnek ve morfoloji zengin.
Bu yüzden, vurgu gibi bağlama bağlı bir olguyu anlamak için token-level deep learning yaklaşımı mantıklı hale geliyor.
-->

---

# Vurguyu Nasıl Tespit Edebiliriz?

## Literatürde iki ana yön var

### 1. Kural tabanlı yaklaşımlar
- Dilbilgisel kurallar kullanır
- Açıklanabilir görünür
- Ama gerçek dil kullanımında kırılgandır

### 2. Makine öğrenmesi / derin öğrenme yaklaşımları
- Veriden örüntü öğrenir
- Daha esnek davranır
- Özellikle bağlamı daha iyi kullanabilir

<!--
Speaker Notes:
Bu problemi çözmek için literatürde iki temel yaklaşım görüyoruz.
Birincisi kural tabanlı yöntemler. Bunlar sezgisel olarak güzel görünür, ama gerçek dil verisinde çok hızlı kırılırlar.
İkincisi makine öğrenmesi ve özellikle derin öğrenme yaklaşımları. Bunlar dili sabit kurallar olarak değil, örüntüler olarak öğrenir.
Pragmatik vurgu ikinci gruba giriyor. Çünkü, çoğu zaman bağlama bağlı ve esnek bir olgudur.
-->

---

# Araştırma Sorusu

Yapay zeka dersi kapsamında başlatılan:

- **Turkish Stress Detection - LLM Token Classification** çalışması,
- daha sonra şu araştırma yönüyle genişletilmiştir:

**Türkçe Dizilim Etiketleme (Sequence Labeling) Görevlerinde Gözetimli Karşıtlamalı Öğrenme (Supervised Contrastive Learning) Destekli Büyük Dil Modelleri: Pragmatik Vurgu Tespiti Üzerine Dağılım Dışı (OOD) Sağlamlık Analizi**

Ana sorularımız:

- `BERT` tabanlı bir sequence labeling modeli Türkçe pragmatik vurguyu öğrenebilir mi?
- `CRF(Conditional Random Fields)`, BIO etiket tutarlılığını anlamlı biçimde artırır mı?
- `[CLS]` üzerinde çalışan **Supervised Contrastive Learning(SCL)**, azınlık sınıfı olan `I-EMPHASIS` için fayda sağlar mı?
- Model, gerçek ve gürültülü Türkçe metinlerde ne kadar dayanıklıdır?

![w:700](assets/research-question.png)

<!--
Visual Idea:
Solda ilk proje kutusu, sağda genişletilmiş araştırma kutusu.
Altında dört araştırma sorusu ikonlarla gösteriliyor.

Speaker Notes:
Bu çalışma önceki bir ders projesinden doğdu, ama aynı problem daha güçlü ve daha araştırma odaklı bir soruya dönüştürüldü.
Artık sadece bir model eğitmek istemiyoruz.
Şunu soruyoruz: bağlamı daha iyi anlayabilir miyiz, etiket dizisini daha tutarlı hale getirebilir miyiz ve en zor azınlık sınıfını daha görünür yapabilir miyiz?
Bu da projeyi basit bir uygulamadan daha kavramsal bir araştırma yönüne taşıyor.
-->

---

# Neden Türkçe Daha Zor?

- Türkçe **eklemeli** bir dildir.
- Tek bir kelime çok fazla dilbilgisel bilgi taşıyabilir.
- Sözcük sırası görece esnektir.
- Aynı bilgi farklı dizilimlerle ifade edilebilir.

Bu yüzden vurgu, yalnızca tek tek kelimelere bakılarak değil, **bağlam ve sıra ilişkisiyle** anlaşılmalıdır.

<!--
Speaker Notes:
Türkçe bu problem için özel olarak zor bir dil.
Birincisi, eklemeli bir dil olduğu için tek bir kelime birçok işlev taşıyabiliyor.
İkincisi, sözcük sırası İngilizce gibi daha katı diller kadar sabit değil.
Bu da şu anlama geliyor: vurgu bazen yalnızca hangi kelimenin geçtiğiyle değil, o kelimenin cümlede nerede durduğuyla ve hangi bağlamda geldiğiyle ilişkili.
Bu yüzden Türkçe için daha bağlam-duyarlı modeller gerekiyor.
-->

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

![w:650](assets/data-strategy.png)

<!--
Visual Idea:
Solda kontrollü sentetik veri bloğu, sağda gerçek ve gürültülü veri bloğu.
İkisi altta “ID + OOD değerlendirme” çizgisinde birleşiyor.

Speaker Notes:
Veri stratejimiz iki parçalıdır.
İlk parça daha kontrollü ve öğrenme için uygun sentetik veri.
İkinci parça ise gerçek dünya koşullarına daha yakın, daha gürültülü OOD verisi.
To address the realism gap, we do not rely only on synthetic data.
Bu iki yapıyı birlikte kullanarak modelin sadece temiz veriyi ezberleyip ezberlemediğini daha iyi anlayabiliyoruz.
-->

---

# Bizim Araştırma Problemimiz

- Bu görev için büyük ve temiz etiketli Türkçe veri az.
- Vurgulu kelimeler, vurgusuz kelimelere göre çok daha az görülüyor.
- Yani veri **dengesiz**: azınlık sınıf problemi var.

Sonuç:

- Dil modelleri çoğunluk sınıfa yaslanabiliyor.
- “Vurgu yok” demek, model için kolay bir kısa yol haline gelebiliyor.
- En kritik bilgi tam da az görülen tarafta kaybolabiliyor.

![w:620](assets/class-imbalance.png)

<!--
Visual Idea:
Büyük bir gri daire içinde çok sayıda “normal” token,
kenarda küçük parlak birkaç “stress” token.

Speaker Notes:
Bizim asıl araştırma problemimiz yalnızca model seçimi değil.
Daha temel bir sorun var: veri kıtlığı ve sınıf dengesizliği.
Yani modelin öğrenmesi gereken en önemli örnekler aslında en az görülen örnekler.
Bu durumda standart dil modelleri çoğu zaman çoğunluk sınıfı öğrenir ve azınlık sınıfı ihmal eder.
Bu nedenle bizim problemimiz, sadece bağlam anlamak değil; az görülen ama anlam açısından kritik olan vurgu örneklerini de görünür hale getirmektir.
-->

---

# Nihai Mimari

`Input -> Tokenizer -> BERTurk -> [CLS] branch -> SCL head -> token branch -> CRF -> BIO output`

- `BERTurk`: bağlamı anlamak için
- `CRF`: BIO etiket dizisini tutarlı hale getirmek için
- `SCL`: azınlık vurgu örneklerini temsil uzayında öne çıkarmak için

![w:860](assets/section3_topology.png)

<!--
Visual Idea:
Ortada BERTurk, yukarı giden `[CLS] -> SCL`, aşağı giden `token states -> CRF`,
en sonda BIO etiketleri. Temiz, tek satırlı akış diyagramı.

Speaker Notes:
Bu slayt mimarinin tek cümlelik özetidir.
Önce cümleyi BERTurk ile bağlamlı biçimde temsil ediyoruz.
Sonra iki farklı ama tamamlayıcı yol açıyoruz.
Bir yol azınlık sınıfı görünürlüğünü artırmaya çalışıyor, diğer yol ise token düzeyinde tutarlı bir etiket dizisi üretmeye odaklanıyor.
Bu yüzden bu yapıyı tek bir model değil, görev paylaşımı yapan bir sistem olarak görmek daha doğru.
-->

---

# Önerdiğimiz Çözüm

## Kavramsal olarak üç parçalı bir yapı öneriyoruz

- **BERT**: cümledeki bağlamı anlamak için
- **CRF**: etiket dizisini daha tutarlı hale getirmek için
- **SCL**: az görülen vurgu örneklerini temsil uzayında daha görünür yapmak için

Buradaki fikir, tek bir sihirli model değil; **birbirini tamamlayan üç bakış açısının birleşimi**dir.

![w:650](assets/solution-synergy.png)

<!--
Visual Idea:
Üç parçalı bir blok diyagram: Context, Sequence, Minority Focus başlıklı üç kutu,
altta birleşip “better stress detection” sonucuna gidiyor.

Speaker Notes:
To address this, we propose a hybrid but conceptually clean solution.
Birinci parça BERT. Bu parça cümlenin bağlamını anlamaya çalışıyor.
İkinci parça CRF. Bu, etiketlerin rastgele değil, dil açısından tutarlı bir sıra oluşturmasını destekliyor.
Üçüncü parça ise supervised contrastive learning. Bunun rolü özellikle az görülen vurgu örneklerini temsil uzayında daha belirgin hale getirmek.
Yani burada amaç tek bir model büyütmek değil, bağlam, sıra ve azınlık sınıf farkındalığını birlikte düşünmek.
-->

---

# Bu Birliktelik Neden Anlamlı?

- BERT tek başına güçlüdür, ama her zaman azınlık sınıfa odaklanmaz.
- CRF dizisel tutarlılık getirir, ama temsil kalitesini tek başına çözmez.
- SCL azınlık örnekleri daha ayırt edilebilir hale getirmeyi hedefler.

Yani:

- **BERT** bağlamı görür,
- **CRF** sırayı düzenler,
- **SCL** “önemli ama az görülen” örnekleri öne çıkarır.

<!--
Speaker Notes:
Burada önemli olan, bu parçaların neden birlikte kullanıldığıdır.
BERT bize bağlam veriyor. Ama bağlamı görmek tek başına yetmeyebilir.
CRF, etiketlerin sırasını daha mantıklı kılıyor. Bu da özellikle sequence labeling görevleri için önemli.
SCL ise asıl zayıf noktaya dokunuyor: azınlık sınıf.
Bu yüzden önerimiz, üç farklı ihtiyacı aynı sistem içinde birleştiren bir araştırma yönüdür.
-->

---

# Vizyon: Bu Çalışma Neye Katkı Sağlayabilir?

- Daha doğal **text-to-speech** sistemleri
- Daha bağlam duyarlı **duygu analizi**
- Niyet ve odak anlayışı daha güçlü sohbet sistemleri
- Türkçe gibi morfolojik olarak zengin diller için daha iyi sequence labeling yaklaşımları

Bu yüzden konu yalnızca bir etiketleme problemi değil; **anlamın ve niyetin daha doğru modellenmesi** problemidir.

![w:650](assets/vision-impact.png)

<!--
Visual Idea:
Dört uygulama kutusu: TTS, sentiment analysis, dialogue systems, Turkish NLP research;
hepsi merkezi “stress-aware language model” kutusuna bağlı.

Speaker Notes:
Bu çalışmanın değeri yalnızca akademik bir etiketleme problemi çözmekten ibaret değil.
Eğer bir sistem vurguyu daha iyi anlarsa, metinden konuşmaya sistemleri daha doğal hale gelebilir.
Duygu analizi yalnızca kelimeleri değil, hangi bilginin öne çıkarıldığını da anlayabilir.
Sohbet sistemleri, kullanıcının neyi vurguladığını daha iyi modelleyebilir.
Bu yüzden bu problem, dilin daha insan-benzeri anlaşılmasıyla ilgilidir.
-->

---

# Sonuç Mesajı

- Pragmatik vurgu, yazılı dilde kaybolan ama anlam için kritik olan bir bilgidir.
- Türkçe bu problemi daha da zorlaştırır.
- Veri kıtlığı ve sınıf dengesizliği, mevcut modelleri zorlar.
- Bu nedenle biz, bağlam + dizi tutarlılığı + azınlık sınıf görünürlüğünü birleştiren bir yön öneriyoruz.

**Kısa mesaj:**

> Bu problemi yalnızca daha güçlü bir modelle değil, Türkçe metindeki anlamı daha dengeli ve daha bilinçli okuyabilen bir yaklaşımla ele almayı öneriyoruz.

<!--
Speaker Notes:
Kapanışta vermek istediğim ana mesaj şu:
Bu proje sadece daha yüksek performanslı bir model arayışı değil.
Asıl amaç, Türkçe metinde kaybolan anlam ağırlığını daha dengeli biçimde yeniden görünür kılmak.
Bu nedenle önerimiz, yalnızca teknik bir kombinasyon değil; bağlamı, diziyi ve azınlık bilgiyi birlikte ciddiye alan bir araştırma yaklaşımıdır.
-->

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
- `Proje-final-raporu.docx`

</div>
</div>

<!--
Speaker Notes:
Son slaytta, bu çalışmanın dayandığı temel araştırma yönlerini ve veri kaynaklarını özetliyorum.
Eğer soru gelirse, özellikle neden BERT, neden CRF ve neden SCL kullandığımızı bu kaynaklar üzerinden açıklayabilirim.
-->

<!--
============================================================
SUNUCU NOT SAYFASI - PDF'DE GORUNMEZ
============================================================

Bu bolum yalnizca sunucu icindir. Sorular geldiginde hizli cevap verebilmek
icin kisaltmalar, terimler ve kavramlar burada ozetlenmistir.

1. KISALTMALAR

- NLP: Natural Language Processing / Dogal Dil Isleme
  Kisa cevap: Bilgisayarin insan dilini anlama ve isleme alani.

- TTS: Text-to-Speech
  Kisa cevap: Yazili metni dogal konusmaya donusturen sistemler.

- OOD: Out-of-Distribution
  Kisa cevap: Egitimde gorulenden farkli, daha gercek ya da daha gurultulu veri dagilimi.

- ID: In-Distribution
  Kisa cevap: Egitim verisine daha cok benzeyen, modelin asina oldugu veri.

- BIO: Begin - Inside - Outside
  Kisa cevap: Dizi etiketlemede kullanilan bir etiketleme semasi.
  Bu projede:
  - B-EMPHASIS = vurgulu bolgenin baslangici
  - I-EMPHASIS = vurgulu bolgenin devami
  - O = vurgu disi token

- SCL: Supervised Contrastive Learning
  Kisa cevap: Ayni siniftaki ornekleri temsil uzayinda yakinlastiran, farkli siniflari ayiran ogrenme yaklasimi.

- CRF: Conditional Random Fields
  Kisa cevap: Etiketlerin tek tek degil, dizi olarak tutarli secilmesini saglayan yapi.

2. TEMEL TERIMLER

- Pragmatik vurgu:
  Kisa cevap: Cumlede hangi bilginin iletisimsel olarak one cikarildigini gosteren odak.
  Birisi "neden pragmatik?" derse:
  Cevap: Cunku bu sadece dilbilgisel degil, konusanin niyeti ve iletisimsel vurgusuyla ilgili.

- Prosodi:
  Kisa cevap: Konusmadaki tonlama, ritim, duraklama ve vurgu yapisi.

- Sequence labeling / dizilim etiketleme:
  Kisa cevap: Cumledeki her tokena bir etiket atama gorevi.

- Token:
  Kisa cevap: Modelin isledigi en temel metin parcasi; kelime ya da alt-kelime olabilir.

- Embedding / temsil uzayi:
  Kisa cevap: Kelime ya da cumlelerin sayisal vektorlerle ifade edildigi uzay.

- Azinlik sinif:
  Kisa cevap: Veri icinde az gorulen ama gorev acisindan onemli olan sinif.
  Bu projede: vurgulu ve ozellikle I-EMPHASIS ornekleri.

- Class imbalance / sinif dengesizligi:
  Kisa cevap: Bazi etiketlerin veri icinde cok, bazilarinin ise cok az gorulmesi durumu.

3. NEDEN BERT?

Soru: Neden BERT kullandiniz?
Kisa cevap:
- Cunku BERT baglami iki yonlu gorur.
- Turkce gibi baglama duyarli ve esnek sozcuk dizilisine sahip bir dilde bu onemlidir.
- Token-level gorevler icin guclu bir temel sunar.

4. NEDEN CRF?

Soru: Neden BERT yeterli degil, neden CRF ekleniyor?
Kisa cevap:
- Cunku sequence labelingde sadece tek tek tokenlari degil, etiket dizisinin mantikli olmasini da isteriz.
- CRF, BIO semasinda anlamsiz gecisleri azaltmaya yardim eder.

5. NEDEN SCL?

Soru: SCL burada ne ise yariyor?
Kisa cevap:
- Veri dengesiz oldugu icin model kolayca cogunluk sinifa kayabilir.
- SCL, az gorulen ama kritik siniflarin temsil uzayinda daha belirgin ayrismasina yardim etmeyi hedefler.

6. NEDEN TURKCE ZOR?

Soru: Bu problem Turkcede neden daha zor?
Kisa cevap:
- Turkce eklemeli bir dil.
- Sozcuk sirasi daha esnek.
- Ayni anlamsal icerik farkli dizilimlerle kurulabiliyor.
- Bu da vurgu ve odagi daha baglam-bagimli hale getiriyor.

7. OOD NE DEMEK, NEDEN ONEMLI?

Soru: OOD'ye neden baktiniz?
Kisa cevap:
- Cunku model sadece temiz ve kontrollu veride iyi gorunebilir.
- Ama gercek hayatta daha farkli, gurultulu ve dagilim disi metinlerle karsilasir.
- OOD testi, modelin gercek dunya dayanikliligini anlamak icin onemlidir.

8. SUNUMDA GELIRSE VERILEBILECEK KISA CEVAPLAR

- "Bu bir sentiment analysis projesi mi?"
  Hayir. Duygu analiziyle iliskili olabilir ama ana hedef, cumlede hangi bilginin odaklandigini bulmaktir.

- "Bu bir speech projesi mi?"
  Dogrudan ses isleme projesi degil. Ama sesli iletisimde bulunan vurgu bilgisinin, yazili metin uzerinden modellenmesine odaklaniyor.

- "En onemli teknik zorluk neydi?"
  Veri kitligi ve sinif dengesizligi. Ozellikle vurgulu tokenlarin az bulunmasi.

- "Bu calismanin pratik degeri ne?"
  Daha dogal TTS, daha hassas duygu analizi ve daha iyi diyalog sistemleri icin altyapi saglayabilir.

- "Bu sunumun tek cümlelik ozet mesaji ne?"
  Turkce yazili metinde kaybolan vurgu bilgisini, baglam, dizi tutarliligi ve azinlik sinif farkindaligini birlestirerek daha iyi modellemeyi oneriyoruz.

9. KELIMEYI YANLIS SOYLEME RISKI OLANLAR

- Pragmatik vurgu
- Prosodi
- Agglutinative / eklemeli dil
- Sequence labeling / dizilim etiketleme
- Conditional Random Fields
- Supervised Contrastive Learning
- Out-of-Distribution

10. SON HATIRLATMA

Sunumda rakam ezberlemek yerine su mantigi koru:
- problem ne?
- neden Turkce zor?
- neden veri sorunu var?
- neden bu uc yapiyi birlikte oneriyoruz?
- bu gelecekte neye katkı saglayabilir?

============================================================
-->
