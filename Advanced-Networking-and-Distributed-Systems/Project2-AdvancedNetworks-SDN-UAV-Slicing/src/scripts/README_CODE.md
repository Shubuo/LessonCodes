# Kod Haritasi

## `run_mininet_uav_experiment.py`

Final Sunumunda kullanilan ana Mininet deney scriptidir. UAV-edge topolojisini kurar, bottleneck linki olusturur, baseline ve priority slicing kosularini calistirir, `iperf` ve `ping` ciktilarindan metrik uretir.

## `run_mininet_policy_sweep.py`

Butunleme icin eklenen yeni deney scriptidir. Uc ilkeyi karsilastirir:

- `baseline_fifo`: Tum akislar ayni FIFO darboğaz kuyruğunda yarismaktadir.
- `source_shaping`: Background source `h3` uzerinden kisitlanir.
- `switch_priority`: Darbogaz cikisinda `tc` HTB siniflari ve IP source filtreleri ile kritik akis onceliklendirilir.

Varsayilan hizli kosu:

```bash
sudo python3 run_mininet_policy_sweep.py
```

Tam queue-size matrisi:

```bash
sudo python3 run_mininet_policy_sweep.py --full
```

## `analyze_policy_sweep.py`

Ilke karsilastirmasi CSV dosyasini okur ve su ciktilari uretir:

- `policy_comparison_table.csv`
- `policy_throughput_results.png`
- `policy_latency_results.png`
- `policy_packet_loss_results.png`
- `policy_jitter_results.png`
- `policy_improvement_vs_baseline.png`
- `policy_sweep_summary.md`

Lokal analiz komutu:

```bash
/opt/miniconda3/bin/python Project2/scripts/analyze_policy_sweep.py \
  --input assets/mininet-policy-sweep/results/measurements.csv \
  --output-dir assets/mininet-policy-sweep/results
```

## Metrikler

- Critical TCP throughput: `iperf` client ciktisindan parse edilir.
- RTT latency: `ping` avg degeri.
- Packet loss: `ping` packet loss yuzdesi.
- Jitter proxy: `ping` mdev/stddev degeri.

## `cli_butunleme_demo.py`

Sunum sirasinda terminalden sorunsuz calistirilmek icin hazirlanan anlatimli demo scriptidir. Canli Mininet kosusu baslatmaz; daha once dogrulanmis CSV sonuc dosyasini okur ve ayni deney akisini adim adim terminalde anlatir.

```bash
python3 Project2/scripts/cli_butunleme_demo.py
```

Beklemesiz hizli kontrol:

```bash
python3 Project2/scripts/cli_butunleme_demo.py --instant
```

## Tekrar Uretilebilirlik

Ham loglar `raw/` klasorunde tutulur. Her deney ismi bandwidth, load factor, queue size, ilke ve repeat bilgisini dosya adinda tasir.
