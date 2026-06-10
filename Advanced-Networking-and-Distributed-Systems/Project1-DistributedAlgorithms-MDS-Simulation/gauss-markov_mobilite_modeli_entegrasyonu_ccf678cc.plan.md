---
name: Gauss-Markov Mobilite Modeli Entegrasyonu
overview: Mevcut statik RGG testlerini Gauss-Markov mobilite modeli ile dinamik senaryolara dönüştürüyoruz. Her zaman adımı için ayrı topoloji oluşturup algoritmaları çalıştıracağız ve performans metriklerini toplayacağız.
todos:
  - id: create_mobility_module
    content: "mobility.py dosyasını oluştur: generate_gauss_markov_trace() ve generate_dynamic_topology() fonksiyonlarını implement et"
    status: completed
  - id: update_visualization
    content: "visualization.py dosyasına mobilite görselleştirme fonksiyonları ekle: plot_mobility_trace() ve plot_dynamic_topology_evolution()"
    status: completed
    dependencies:
      - create_mobility_module
  - id: refactor_main_experiments
    content: "project-mds.py'deki run_experiments() fonksiyonunu yeniden yapılandır: statik RGG testlerini kaldır, mobilite senaryoları ekle, her zaman adımı için algoritmaları çalıştır"
    status: completed
    dependencies:
      - create_mobility_module
  - id: add_mobility_metrics
    content: Performans metriklerine mobilite ve topoloji değişim metriklerini ekle (topology_stability, connection_changes, avg_mds_over_time)
    status: completed
    dependencies:
      - refactor_main_experiments
  - id: update_visualization_performance
    content: visualization.py dosyasına plot_mobility_performance() fonksiyonunu ekle ve plot_comprehensive_results() fonksiyonunu mobilite metrikleriyle güncelle
    status: completed
    dependencies:
      - add_mobility_metrics
  - id: update_analysis
    content: "analysis.py dosyasını güncelle: mobilite senaryoları için özel analiz bölümü ekle ve raporlama fonksiyonlarını güncelle"
    status: completed
    dependencies:
      - add_mobility_metrics
---

# Gauss-Markov Mobilite Modeli Entegrasyonu

## Genel Bakış

Mevcut projede statik RGG (Random Geometric Graph) testleri var. Bu testleri **Gauss-Markov mobilite modeli** ile dinamik drone hareket senaryolarına dönüştüreceğiz. Her zaman adımı için ayrı topoloji oluşturulacak ve algoritmalar her zaman adımında çalıştırılarak performans metrikleri toplanacak.

## Değişiklikler

### 1. Yeni Mobilite Modülü Oluşturma

**Dosya:** `mobility.py` (yeni)

- **`generate_gauss_markov_trace()`**: Gauss-Markov hareket modeli ile mobilite izi üretir
- 3D uzay: 1000m × 1000m × 200m
- Parametreler: N=20-50 drone, R=150m menzil, V=10-25 m/s hız, T=600 saniye
- Her drone için başlangıç pozisyonu ve hız vektörü
- Alpha=0.85 ile Gauss-Markov güncellemesi
- Sınır kontrolü (bounce veya wrap-around)
- Pandas DataFrame döndürür: `[time, node_id, x, y, z, vx, vy, vz]`
- **`generate_dynamic_topology()`**: Mobilite izinden dinamik topoloji oluşturur
- Her zaman adımı (t) için komşuluk matrisi hesaplar
- Öklid mesafesi ile 150m menzil kontrolü
- NetworkX grafına dönüştürür
- Dictionary döndürür: `{time: Graph}`

### 2. visualization.py Güncellemeleri

**Dosya:** `visualization.py`

- **`generate_drone_network()` fonksiyonunu güncelle**: 
- Mevcut statik RGG üretimini koru (Gnutella için gerekli)
- Mobilite parametrelerini kaldır (artık `mobility.py`'de)
- **Yeni fonksiyon:** `plot_mobility_trace()`: 
- Mobilite izini 3D veya 2D projeksiyon olarak görselleştirir
- Drone yollarını zaman içinde gösterir
- **Yeni fonksiyon:** `plot_dynamic_topology_evolution()`:
- Topoloji değişimini zaman içinde gösterir
- Farklı zaman anlarında (t=0, t=300, t=600) topoloji görselleştirmesi

### 3. project-mds.py Ana Değişiklikler

**Dosya:** `project-mds.py`

- **`run_experiments()` fonksiyonunu yeniden yapılandır**:
- Statik RGG testlerini kaldır
- Yeni mobilite senaryoları ekle:
    - `Mobile_Small_Swarm`: 20 drone, 600 saniye
    - `Mobile_Medium_Swarm`: 35 drone, 600 saniye  
    - `Mobile_Large_Swarm`: 50 drone, 600 saniye
- **Her mobilite senaryosu için**:

1. `generate_gauss_markov_trace()` ile mobilite izi üret
2. `generate_dynamic_topology()` ile dinamik topolojiler oluştur
3. Her zaman adımı (t) için:

    - `run_seq_mds(G_t)` çalıştır
    - `run_span_mds_simulation(G_t)` çalıştır
    - Sonuçları topla (MDS boyutu, süre, mesaj sayısı)

4. Tüm zaman adımları için ortalamaları hesapla
5. Topoloji değişim metriklerini ekle (bağlantı sayısı, ortalama derece)

- **Yeni metrikler**:
- `avg_mds_size_over_time`: Zaman içinde ortalama MDS boyutu
- `topology_stability`: Topoloji değişim oranı
- `connection_changes`: Zaman adımı başına bağlantı değişim sayısı

### 4. visualization.py Performans Görselleştirmeleri

**Dosya:** `visualization.py`

- **`plot_comprehensive_results()` güncelle**:
- Mobilite metriklerini ekle (topoloji stabilitesi, bağlantı değişimleri)
- **Yeni fonksiyon:** `plot_mobility_performance()`:
- Zaman içinde MDS boyutu değişimi
- Zaman içinde algoritma performansı (süre, mesaj sayısı)
- Topoloji değişim grafikleri

### 5. analysis.py Güncellemeleri

**Dosya:** `analysis.py`

- **`save_findings_to_file()` güncelle**:
- Mobilite senaryoları için özel analiz bölümü ekle
- Topoloji stabilitesi ve mobilite etkilerini raporla
- **Yeni metrikler**:
- Mobilite sırasında algoritma davranışı
- Topoloji değişimlerinin MDS boyutuna etkisi

## Teknik Detaylar

### Gauss-Markov Modeli

```python
# Hız güncellemesi
v_new = α * v_old + (1-α) * v_mean + sqrt(1-α²) * noise

# Pozisyon güncellemesi  
p_new = p_old + v_new * Δt
```



### Dinamik Topoloji

- Her zaman adımında mesafe matrisi hesaplanır
- 150m menzil içindeki düğümler bağlanır
- NetworkX grafı oluşturulur

### Performans Ölçümü

- Her zaman adımı için algoritma çalıştırılır
- Sonuçlar toplanır ve ortalamaları hesaplanır
- Topoloji değişim metrikleri eklenir

## Dosya Yapısı

```javascript
Dist.Alg/
├── mobility.py          # YENİ: Mobilite modeli ve dinamik topoloji
├── project-mds.py        # GÜNCELLENECEK: Ana deney fonksiyonu
├── visualization.py      # GÜNCELLENECEK: Görselleştirme fonksiyonları
├── analysis.py           # GÜNCELLENECEK: Analiz ve raporlama
├── algorithms.py         # DEĞİŞMEYECEK: Algoritma implementasyonları
└── distsim.py           # DEĞİŞMEYECEK: Simülasyon framework
```



## Test Senaryoları

1. **Mobile_Small_Swarm**: 20 drone, 600s, mobilite
2. **Mobile_Medium_Swarm**: 35 drone, 600s, mobilite  