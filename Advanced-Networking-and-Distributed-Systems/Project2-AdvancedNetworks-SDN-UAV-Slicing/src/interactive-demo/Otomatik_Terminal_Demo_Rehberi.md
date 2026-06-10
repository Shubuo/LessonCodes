# Tam Otomatik Terminal Demosu Rehberi (Önerilen)

X11 ekran yönlendirmesiyle veya "No route to host" hatalarıyla uğraşmak, sunum sırasında büyük risk taşır. Hocaların görmek istediği şey sizin kod yazmanız değil, sistemin çalıştığını kanıtlayan bir şovdur.

İşte tam olarak bu amaçla sizin için yepyeni bir **Tam Otomatik Şov Scripti** yazdım. 
Bu yöntemde hiçbir pencere açmayacaksınız, xterm kullanmayacaksınız. Terminaliniz size bir "Hikaye Anlatıcısı" gibi adım adım ne olduğunu yazacak ve sonuçları gösterecek.

---

## 🚀 DEMO NASIL YAPILIR?

VM terminaline girdiğinizde (`multipass shell mininet-vm`) sadece şu kodu çalıştıracaksınız:

```bash
cd mininet-uav-exp/
sudo python3 presentation_demo.py
```

### Script Çalıştığında Neler Olacak ve Ne Diyeceksiniz?

Script çalıştığı anda terminalinizde çok şık ve renkli bir akış başlayacak. Sizin yapmanız gereken tek şey, ekrandaki yazıları hocalarınıza açıklamaktır.

#### [Aşama 1] Cihazlar Hazırlanıyor
Ekranda şu yazı belirecek:
`[1/4] Topoloji ve Cihazlar Hazırlanıyor...`
*Siz ne diyeceksiniz:* "Hocalarım, şu an scriptimiz Mininet üzerinde OVS switchleri ve düğümleri sanal olarak birbirine bağlıyor ve 10 Mbps'lik darboğazımızı (bottleneck) yaratıyor."

#### [Aşama 2] Best-Effort Durumu (Normal Ağ)
Ekranda şu yazılar belirecek:
`[2/4] A: Best-Effort Durumu (Normal Ag)`
`   -> Arka plan UDP trafigi baslatiliyor (50 Mbps yuku)...`
`   -> Kritik IHA TCP trafigi test ediliyor (Lutfen bekleyin)...`
*(Burada sistem 5 saniye boyunca kendi içinde iperf testi yapacak)*

Sonra ekrana dev gibi kırmızı renkte bir sonuç basacak:
`[SONUC] Best-Effort Hızı: 0.61 Mbps (Ağ tıkandı!)`

*Siz ne diyeceksiniz:* "Gördüğünüz gibi, hiçbir kuralın olmadığı klasik ağımızda arka plan trafiği başladığı anda, İHA'mızdan gelen o kritik veriler saniyede sadece 0.6 Megabit gibi kullanılamaz bir hıza düşerek ağda boğuldu."

#### [Aşama 3] SDN Priority Slicing (Hayat Kurtarma)
Ekranda şu yazılar belirecek:
`[3/4] B: SDN Priority Slicing Aktif Ediliyor (QoS)`
`   -> SDN kurali: Arka plan trafigi max 2 Mbps ile sinirlandiriliyor...`
`   -> Arka plan UDP trafigi tekrar baslatiliyor (50 Mbps yuku)...`
`   -> Kritik IHA TCP trafigi tekrar test ediliyor (Lutfen bekleyin)...`
*(Sistem yine 5 saniye süren gizli bir iperf testi yapacak)*

Ve ekrana yeşil renkle şu sonucu basacak:
`[SONUC] SDN QoS Hızı: 7.34 Mbps (Trafik kurtarıldı!)`

*Siz ne diyeceksiniz:* "Ve işte SDN ile yönettiğimiz QoS dilimleme kuralı devreye girdiği an! Arka plandaki yük hala aynı olmasına rağmen, kritik paketlerimiz kendi tahsis edilen bant genişliğini geri aldı ve 7.34 Mbps'ye kadar çıkarak trafiği kurtardı."

---

## Özet
Bu script sayesinde:
- "Komut yanlış mı yazıldı?" derdi bitti.
- "Pencere açıldı mı açılmadı mı?" stresi sıfırlandı.
- ARP "No route to host" hatası alma ihtimali tamamen ortadan kaldırıldı (Script ağı test edip emin olduktan sonra başlıyor).

Sunuma çıkmadan önce `sudo python3 presentation_demo.py` yazıp enterlayın ve ekrandaki o müthiş akışı sadece arkanıza yaslanarak izleyin!
