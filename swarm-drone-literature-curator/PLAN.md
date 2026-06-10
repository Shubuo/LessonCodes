# Swarm Drone Literature Curator - Plan

Bu proje (eski `seminar` klasörü), Sürü Dronlar (Swarm Drones) ve çoklu ajan sistemleri (Multi-Agent Systems) üzerine akademik literatür taramasını, özetlenmesini ve otomatik sunum/rapor üretilmesini hedefleyen bir küratör yapıya dönüştürülecektir.

## 1. Amaç
- Swarm Drone literatüründeki akademik makalelerin PDF formatında toplanması.
- Makalelerin yapay zeka (LLM) araçlarıyla analiz edilerek önemli bulguların, metodolojilerin ve sonuçların yapılandırılmış bir formatta (örn. JSON veya Markdown) saklanması.
- Çıkarılan özetlerin düzenli olarak Marp tabanlı sunumlara (.md) veya otomatik raporlara (.docx/.pdf) dönüştürülmesi.

## 2. Mimari ve Bileşenler
- **`papers/`**: İndirilen ham PDF makalelerinin (Örn: IEEE, arXiv) tutulduğu veri havuzu.
- **`extractors/`**: PDF'leri okuyup metin çıkaran ve LLM'e (Gemini/OpenAI) gönderen scriptler.
- **`curated_knowledge/`**: LLM tarafından üretilen makale analiz raporları ve yapılandırılmış metadatalar.
- **`presentation_builder/`**: `curated_knowledge` klasöründeki verileri kullanarak otomatik olarak Marp (Markdown) sunum kodları ve CSS üreten modül.

## 3. Yol Haritası (Roadmap)
- [ ] Mevcut `swarm_drone_literature_review.marp.md` dosyası ve raporlarının yapısal analizinin yapılıp yeni mimariye yedirilmesi.
- [ ] Makale indirme (veya var olanları okuma) botunun yazılması.
- [ ] Marp derleme betiğinin (`build_marp_pdf.sh`) daha esnek bir hale getirilmesi.
- [ ] Sistemin CLI (Command Line Interface) üzerinden kullanılabilir hale getirilmesi (Örn: `python run_curator.py --generate-presentation`).
