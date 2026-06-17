# Butunleme Multipass Runbook

Bu dosya butunleme deneylerini `mininet-vm` uzerinde tekrar calistirmak icin kullanilir. VM restart edilmez; sadece erisim ve deney komutlari calistirilir.

## 1. VM Erisim Kontrolu

```bash
multipass exec mininet-vm -- bash -lc 'hostname; which mn; which iperf; cd /home/ubuntu/mininet-uav-exp && ls -la'
```

Beklenen:

- `mininet-vm`
- `/usr/bin/mn`
- `/usr/bin/iperf`
- `/home/ubuntu/mininet-uav-exp`

## 2. Yeni Scripti VM'e Aktarma

```bash
multipass transfer 'Butunleme/Project2/scripts/run_mininet_policy_sweep.py' mininet-vm:/home/ubuntu/mininet-uav-exp/run_mininet_policy_sweep.py
```

## 3. Hizli Ilke Karsilastirmasi Kosusu

```bash
multipass exec mininet-vm -- bash -lc 'cd /home/ubuntu/mininet-uav-exp && sudo mn -c && sudo python3 run_mininet_policy_sweep.py'
```

Bu kosu 27 deney uretir:

```text
1 bandwidth * 3 load factors * 1 queue size * 3 ilke * 3 repeats = 27
```

## 4. Tam Ilke Karsilastirmasi Kosusu

Zaman varsa:

```bash
multipass exec mininet-vm -- bash -lc 'cd /home/ubuntu/mininet-uav-exp && sudo mn -c && sudo python3 run_mininet_policy_sweep.py --full'
```

Bu kosu 81 deney uretir.

## 5. Sonuclari Lokale Cekme

```bash
mkdir -p 'Butunleme/assets/mininet-policy-sweep'
multipass transfer -r mininet-vm:/home/ubuntu/mininet-uav-exp/policy_sweep 'Butunleme/assets/mininet-policy-sweep/results'
```

## 6. Lokal Analiz

```bash
/opt/miniconda3/bin/python 'Butunleme/Project2/scripts/analyze_policy_sweep.py' \
  --input 'Butunleme/assets/mininet-policy-sweep/results/measurements.csv' \
  --output-dir 'Butunleme/assets/mininet-policy-sweep/results'
```
