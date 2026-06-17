# Presentation Skill

Bu dosya, `metropolis-ege.css` temasını kullanarak akademik ve teknik sunum üretmek için tekrar kullanılabilir çalışma standardıdır. Amaç, düz metin veya ders notu benzeri içerikleri doğrudan görsel, tutarlı ve sunulabilir bir slayt destesine dönüştürmektir.

## Amaç

- Girdi metnini analiz edip slayt omurgasına dönüştürmek
- `metropolis-ege.css` temasına sadık kalmak
- Hem bağımsız `HTML` hem de `Marp Markdown` üretmek
- Gerekirse `assets/` altında yerel görseller, SVG diyagramlar ve makale figürleri oluşturmak
- Sunum sonunda tek sayfalık `IEEE` referans slaytı üretmek
- sunum içeriğindeki sayfalarda görsel ve içeriklerin hizalı olması
- sunum sayfasından taşma olmayacak şekilde, metin ve görsel boyutlarının ölçeklendirilmesi

## Beklenen Girdiler

- Ana içerik dosyası: `.txt`, `.md` veya yapılandırılmamış notlar
- Tema dosyası: `metropolis-ege.css`
- Varsa üst klasörde veya çalışma alanında ilgili makaleler: `.pdf`
- Kullanıcıdan gelebilecek ek istekler:
  - kapak iyileştirme
  - daha görsel sunum
  - Türkçe karakter düzeltme
  - referans slaytı
  - Marp çıktı

## Zorunlu Çıktılar

- `sunum.html`
- `sunum.md`
- `assets/` klasörü
- Kullanılan görsellerin yerel kopyaları veya özel üretilmiş SVG'leri

## Varsayılan Çalışma Akışı

1. Çalışma klasöründeki ana metin dosyasını bul.
2. `metropolis-ege.css` dosyasını incele ve mevcut sınıfları kullan.
3. İçeriği analiz ederek şu iskeleti çıkar:
   - problem
   - yöntem
   - mimari
   - senaryo / veri akışı
   - öneri katmanı
   - sonuç
4. Varsa ana ve ya üst klasördeki ilgili PDF makaleleri bul ve ilk sayfalardan bibliyografik bilgileri çıkar.
5. Gerekli görselleri belirle:
   - mümkünse özel SVG diyagram üret, SVG metinleri hizalı olmalı, şekil dışında metinler taşmamalı.
   - varsa ilgili makale figürlerini yerel `assets/` içine çıkar
6. Sunumu önce görsel ve içerik mantığı açısından düzenle.
7. Sonra aynı yapıyı `sunum.md` içine Marp uyumlu olarak aktar.
8. En sona tek sayfalık `Referanslar` slaytı ekle.

## Tasarım Kuralları

- Tema renklerini bozma; `metropolis-ege.css` ana görsel dil olarak kalmalı.
- Kapak slaytında gereksiz açıklama metinlerini kaldır, güçlü bir başlık hiyerarşisi kur.
- İlk slaytta konuya özgü bir hero görsel bulundur.
- Her slaytta metin yoğunluğunu azalt:
  - 3-5 ana madde hedefle
  - uzun paragraf yerine kart, diyagram, tablo, karşılaştırma kullan
- Teknik slaytlarda mümkün olduğunca şu yapıları kullan:
  - akış diyagramı
  - karar matrisi
  - 2x2 karşılaştırma
  - metrik kartları
- Aynı slaytta hem çok uzun metin hem de çok büyük tablo kullanma.

## İçerik Dönüştürme Kuralları

- Ham metni birebir yapıştırma.
- Cümleleri sunum diline indir:
  - daha kısa
  - daha vurucu
  - kavram odaklı
- Akademik anlamı bozma.
- Teknik doğruluk korunmalı.
- Bir yöntemin amacı, girdisi, çıktısı ve rolü ayrı ayrı görünür olmalı.
- markdown dosyası içine sunumla ilgili okuyucu notları koyulmalı. 
- Okuyucu notları sunucunun direk bu notları okuyarak sunumu yapabileceği nitelikte olmalı. 

## Görselleştirme Kuralları

- Öncelik sırası:
  1. özel üretilmiş SVG diyagramlar
  2. makalelerden alınan ilgili figürlerin yerel kopyaları, sadece görsel olan kısımların kırpılmış hali.
  3. İnternette bulunan dış kaynak görsellerin yerel kopyaları
- Görseller mutlaka `assets/` altında tutulmalı.
- Görseller temayla uyumlu, temiz ve okunabilir olmalı.
- Dış kaynaktan görsel kullanılacaksa mümkünse açık lisanslı veya güvenli kullanım sunan kaynaklar tercih edilmeli.
- Slayt içi görsel atıflar kısa biçimde `[1]`, `[2]` gibi verilmeli.

## Türkçe Dil Kuralları

- UTF-8 Türkçe karakterler kullanılmalı.
- `ğ, ü, ş, ı, ö, ç, İ` gibi karakterleri ASCII'ye düşürme.
- Başlık ve gövde metni doğal Türkçe okunmalı.
- Teknik terimler gerekirse İngilizce bırakılabilir, ancak bağlam Türkçe olmalı.

## HTML Üretim Kuralları

- `sunum.html` bağımsız tarayıcı sunumu olmalı.
- `metropolis-ege.css` doğrudan bağlanmalı.
- Tema dışında gerekli yardımcı stiller minimal seviyede eklenmeli.
- Slayt yapısı 16:9 görünümünü korumalı.
- Mobilde tamamen bozulmayan, masaüstünde güçlü görünen bir düzen kurulmalı.

## Marp Markdown Kuralları

- `sunum.md` içinde şu frontmatter bulunmalı:

```yaml
---
marp: true
theme: metropolis-ege
paginate: true
size: 16:9
lang: tr
html: true
---
```

- Slayt ayracı olarak `---` kullanılmalı.
- Tema sınıflarını kullanmak için gerektiğinde HTML blokları kullanılabilir.
- HTML ve Markdown sunum arasında içerik tutarlılığı korunmalı.

## Referans Kuralları

- Üst klasördeki ilgili PDF makaleler varsa mutlaka kontrol et.
- Başlık, yazar, dergi, cilt, sayfa veya makale numarası, yıl ve DOI bilgilerini çıkar.
- Son slayt `Referanslar` olmalı.
- Kullanıcı aksini istemedikçe referanslar tek sayfada tutulmalı.
- Biçim `IEEE` olmalı.
- Slayt içi atıf numaraları referans slaytıyla eşleşmeli.

## Önerilen Slayt İskeleti

1. Kapak
2. Problem ve motivasyon
3. Mimari veya yöntem akışı
4. Ana model / ana yöntem açıklaması
5. Veri akışı / karar mantığı
6. Uygulama veya öneri paradigması
7. Vaka örnekleri
8. Sonuç ve mühendislik çıkarımı
9. Referanslar

## Kalite Kontrol Listesi

- [ ] Kapakta gereksiz metin yok
- [ ] Türkçe karakterler doğru
- [ ] `assets/` içindeki tüm görseller dosya olarak mevcut
- [ ] `sunum.html` içindeki tüm görsel yolları çalışıyor
- [ ] `sunum.md` Marp ile export edilebilir yapıda
- [ ] Tüm kısa atıflar referans slaydındaki numaralarla eşleşiyor
- [ ] Referans slaytı tek sayfaya sığıyor
- [ ] Her slayt görsel olarak dengeli
- [ ] Metin yoğunluğu sunum için uygun

## Bu Proje İçin Kullanılan Referans Temeli

Bu klasördeki sunumlarda aşağıdaki çizgi korunmalı:

- Hibrit PV arıza tespiti: `LSTM-Autoencoder + Random Forest`
- Bakım tavsiye ve temizlik planlama: rolling-horizon recommendation
- PV operasyon ve bakım bağlamı: O&M review
- Knowledge-based recommendation paradigması: recommender review

## Kullanım Notu

Bu dosya resmi sistem `skill` kaydı değildir; ancak aynı klasörde bulunan sunum üretim standardı olarak kullanılmalıdır. Gelecekte kullanıcı “bu skill’e göre sunum hazırla” dediğinde, bu dosyadaki kurallar doğrudan uygulanmalıdır.
