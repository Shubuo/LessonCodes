# Project Status & Rules (Auto-Compacted)

## 📌 Son Güncelleme
- **Tarih:** 2026-06-10
- **Son Tamamlanan State:**
  - Mininet SDN İHA (UAV) Edge dilimleme (slicing) projesi başarıyla tamamlandı. Terminal tabanlı tam otomatik canlı `iperf` takibi sağlayan Python demosu (`cli_demo.py` ve `presentation_demo.py`), tarayıcıda çalışan interaktif HTML/JS/CSS paneli (`interactive-demo/index.html`) ve topoloji görselleri oluşturuldu.
  - Mininet Python 3 uyumluluğu için oluşan `TypeError` (bytes-string) hatası base64 decode yöntemiyle kalıcı olarak çözüldü.
  - Akademik final raporu olan `Final-Report.tex` (eski adıyla `conference_101719.tex`) dosyası IEEE formatında, İngilizce olarak tamamen güncellenerek PDF (`Final-Report.pdf`) olarak derlendi. Görseller (figürler) PNG formatında kırpılarak (cropped) okunabilirlik artırıldı ve Senaryo B mimari şeması dahil edildi.

## 🛠 Mevcut Mimari ve Kurallar
- **Mimari:** Mininet sanal makinesi (Multipass Ubuntu VM) üzerinde Python scriptleri ile `OVSController` kullanılarak SDN simülasyonu çalıştırılıyor. `autoStaticArp=True` parametresiyle "No route to host" ARP sorunları aşıldı. Ağ darboğazı (10Mbps, 20ms delay, `use_htb=True`) `s1` ve `s2` switch'leri arasında kuruludur.
- **Trafik Yönetimi:** QoS önceliklendirmesi (Priority Slicing) `tc qdisc` (Traffic Control) kullanılarak arka plan trafiğine sahip olan `h3` düğümü üzerinde `tbf rate 2mbit burst 32kbit latency 50ms` parametreleriyle limitlenerek garanti altına alınmaktadır.
- **Rapor Formatı:** Rapor IEEE Conference Proceedings şablonuna göre yazılmakta olup `.tex` üzerinden yönetilmektedir.
- **Kural 1 (Sunum Tercihi):** `Mininet_Second_Presentation_BurakYoruk.md` referans alınarak ilerlenmektedir. Manuel xterm pencereleri yerine tam otomatik hatasız scriptler kullanılmalıdır.

## 🔄 Aktif Geliştirme Süreci (Current Task)
- Rapor, simülasyon sonuçları, CLI demosu ve interaktif panel teslim (EgeDers) için tamamen hazırdır. 
- Gereksiz/gizli dosyalar ayıklanarak son teslim arşivi olan `mininet_sdn_uav_code_env.zip` başarıyla güncellenmiştir.

## ⚠️ Bilinen Sorunlar / Teknik Borçlar
- Mininet'te `Reference Controller` TCP paketlerini düşürdüğü için `OVSController` kullanmak zorunludur. `mn -c` komutu ile Mininet ağını her test sonrası temizlemek, arka planda takılı `iperf` süreçlerini temizlemek ve `RTNETLINK File exists` hatasını önlemek için kritiktir.
- Terminal ortamında kopyala-yapıştır yaparken `nano` editörü Python kodlarında "staircase effect" (girinti kayması) yarattığı için, kodlar VM'e aktarılırken `base64` decode veya raw string output metotları tercih edilmelidir.

## 🚀 Bütünleme İyileştirmeleri (Yeni Versiyon Özeti)

Final Sunumunda Mininet üzerinde UAV kaynaklı kritik TCP trafiğin background UDP trafik altında nasıl etkilendiği incelenmişti. Bütünleme için yapılan teknik iyileştirmeler şunlardır:

1. **İlke Çeşitliliği:** Eski source-side shaping (kaynakta şekillendirme) yaklaşımına ek olarak **switch-side priority** (anahtar taraflı önceliklendirme) ilkesi tasarlandı.
2. **Kapsamlı Testler:** Background load factor `1x`, `2x`, `3x` olacak şekilde yeni deney seti oluşturuldu (toplam 27 Mininet koşusu).
3. **Sonuç:** En ağır tıkanıklık koşulu olan `3x` background load altında, baseline FIFO ilkesinde kritik akışın RTT değeri 108 ms ve packet loss %30 iken, yeni `switch-side priority` yaklaşımında RTT 24 ms, packet loss %0 olarak ölçülmüş ve başarısı kanıtlanmıştır.

VM üzerinde yeni deneyi tekrar üretmek için `src/scripts/run_mininet_policy_sweep.py` betiği eklendi. Yapılan tüm iyileştirmeler ve sonuçlar ana `reports/Butunleme-Report.pdf` (IEEE) dosyasına entegre edilmiştir. Ayrıca sunum dosyaları `presentation/` klasöründe yer almaktadır.
