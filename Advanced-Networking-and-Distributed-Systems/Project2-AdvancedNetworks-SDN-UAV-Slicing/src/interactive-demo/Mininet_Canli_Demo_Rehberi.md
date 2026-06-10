# Mininet Canlı Demo Rehberi (Kusursuz Yöntem)

İsteğiniz üzerine **en ideal senaryoyu** hazırladım: Topolojiyi sıfırdan oluşturmakla uğraşmayacaksınız, kendi kodunuzla birebir aynı yapıyı kurup sizi hazır şekilde komut ekranına (CLI) bırakan **özel bir canlı demo scripti** (`demo_topology.py`) oluşturdum. 

Böylece hocalarınız hem terminal komutlarını ve akan sayıları canlı izleyecek, hem de siz arka planda topoloji ayarlarıyla zaman kaybetmemiş olacaksınız.

---

## 🖥️ ÖN HAZIRLIK: XQuartz ile Ekran Bağlantısı
Canlı izletim için pencereleri Mac ekranınıza yansıtmalıyız. Sunumdan önce şu adımları yapın:

1. Mac'inizde **XQuartz** uygulamasını açın.
2. Üst menüden **XQuartz -> Preferences (Tercihler) -> Security (Güvenlik)** sekmesindeki **"Allow connections from network clients"** kutucuğunu işaretleyin. (Sonra XQuartz'ı tamamen kapatıp yeniden açın).
3. Mac terminalinizi açıp şu komutu yazın:
   ```bash
   xhost +
   ```
4. VM'e girin (`multipass shell mininet-vm`) ve görüntü yönlendirmesini aktif edin:
   ```bash
   export DISPLAY=$(ip route | awk '/default/ {print $3}'):0
   ```
*(Test için `xeyes` veya `xterm` yazıp enterladığınızda Mac ekranınızda açılıyorsa hazırsınız demektir).*

---

## 🚀 CANLI DEMO ADIMLARI

### Adım 1: Hazır Topolojiyi Ayağa Kaldırmak
VM içindeyken özel demo scriptini çalıştırın:
```bash
cd mininet-uav-exp/
sudo python3 demo_topology.py
```
Bu script sizin için otomatik olarak;
- `h1` (İHA), `h2` (Edge), `h3` ve `h4` cihazlarını yaratır.
- Aralarına 10 Mbps'lik tam sizin deneyinizdeki darboğazı kurar.
- Ekrana ne yapmanız gerektiğine dair bir "Kopya Kağıdı" basar ve sizi `mininet>` komut satırında bırakır.

### Adım 2: Görsel Ekranları (xterm) Açmak
`mininet>` komut satırı açıldığında, 4 cihazın da ekranını Mac'inize çağırmak için şunu yazın:
```bash
mininet> xterm h1 h2 h3 h4
```
*Açılan 4 küçük siyah pencereyi ekrana dizin. Jüriye "h1 İHA'mız, h2 ise Edge sunucumuz" şeklinde cihazları tanıtın.*

### Adım 3: Kritik Trafiği Başlatmak (İzleme Aşaması)
1. **h2 (Sunucu) Penceresine tıklayın ve şunu yazın:**
   ```bash
   iperf -s -i 1
   ```
2. **h1 (İHA) Penceresine tıklayın ve şunu yazın:**
   ```bash
   iperf -c 10.0.0.2 -t 300 -i 1
   ```
*Seyirciye ne diyeceksiniz:* "Şu an İHA'mız saniyede yaklaşık 10 Megabit ile kesintisiz veri aktarıyor. Lütfen h1 penceresindeki sağdaki `Mbits/sec` sütununa dikkat edin."

### Adım 4: Tıkanıklık (Best-Effort Çöküşü) Yaratmak
Kritik veri akarken arka planda ağı boğacağız.
1. **h4 Penceresine tıklayın ve şunu yazın:**
   ```bash
   iperf -s -u -i 1
   ```
2. **h3 Penceresine tıklayın ve şunu yazın:**
   ```bash
   iperf -c 10.0.0.4 -u -b 50M -t 100
   ```
*Seyirci ne görecek:* h1 (İHA) penceresindeki o yüksek TCP sayıları bir anda çökecek, veri akışı durma noktasına gelecektir. (Örneğin 10 Mbps'den 0.5 Mbps'ye düşecek).

*Seyirciye ne diyeceksiniz:* "Kritik olmayan devasa bir arka plan trafiği başladığı anda, geleneksel ağımız eşitlikçi (best-effort) davrandığı için drone'dan gelen hayati verilerin hızı sıfıra yaklaştı ve ağımız tıkandı."

### Adım 5: SDN QoS ile Canlı Kurtarma Operasyonu
Ağ tıkanık durumdayken, ana Mininet terminalinize (scriptin sizi bıraktığı yer) dönün ve şu kuralı kopyalayıp yapıştırın (Zaten script çalıştığında bu komutu ekrana hatırlatıcı olarak basmış olacak):
```bash
mininet> sh tc qdisc add dev s1-eth1 root tbf rate 10mbit burst 10kb
```
*Seyirci ne görecek:* Komut girildikten saniyeler sonra h1 penceresindeki çökmüş olan hız tekrar 7-9 Mbps bandına fırlayacak ve o hızda kilitlenecektir.

*Seyirciye ne diyeceksiniz:* "SDN tabanlı QoS kuralımızı devreye soktuğum anda, arka plan trafiği hala ağa yükleniyor olmasına rağmen kritik trafiğimiz kendisine tahsis edilen bandı geri aldı ve stabil akışına geri döndü."

Demoyu bitirmek için ana terminalde `exit` yazmanız yeterlidir.
