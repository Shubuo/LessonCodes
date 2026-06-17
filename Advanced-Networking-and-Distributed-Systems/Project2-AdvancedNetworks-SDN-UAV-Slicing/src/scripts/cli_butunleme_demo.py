#!/usr/bin/env python3
"""
Bütünleme sunumu için güvenli CLI demo.

Bu script canlı Mininet deneyi başlatmaz. Sunum sırasında sorun çıkmaması için
daha önce üretilmiş ve doğrulanmış `policy_comparison_table.csv` dosyasını okur,
deney akışını terminalde adım adım anlatır ve en ağır tıkanıklık senaryosunun
sonuçlarını açıklar.

Kullanım:
    python3 Project2/scripts/cli_butunleme_demo.py
    python3 Project2/scripts/cli_butunleme_demo.py --instant

Sunumda söylenebilecek kısa açıklama:
    "Bu demo canlı Mininet'i yeniden başlatmıyor; bunun yerine az önce rapora
    koyduğum doğrulanmış deney çıktısını terminalde tekrar oynatıyor. Böylece
    deney mantığını ve sonuçları adım adım gösterebiliyorum."
"""

import argparse
import csv
import sys
import time
from pathlib import Path


POLICY_LABELS = {
    "baseline_fifo": "Baseline FIFO",
    "source_shaping": "Source shaping",
    "switch_priority": "Switch-side priority",
}

FALLBACK_ROWS = [
    {
        "policy": "baseline_fifo",
        "avg_throughput_mbps": "3.551",
        "avg_latency_ms": "108.005",
        "avg_packet_loss_pct": "30.000",
        "avg_jitter_ms": "24.502",
        "throughput_gain_vs_baseline_pct": "0.00",
        "latency_reduction_vs_baseline_pct": "0.00",
    },
    {
        "policy": "source_shaping",
        "avg_throughput_mbps": "7.370",
        "avg_latency_ms": "44.084",
        "avg_packet_loss_pct": "0.000",
        "avg_jitter_ms": "0.116",
        "throughput_gain_vs_baseline_pct": "107.55",
        "latency_reduction_vs_baseline_pct": "59.18",
    },
    {
        "policy": "switch_priority",
        "avg_throughput_mbps": "7.613",
        "avg_latency_ms": "24.059",
        "avg_packet_loss_pct": "0.000",
        "avg_jitter_ms": "0.039",
        "throughput_gain_vs_baseline_pct": "114.39",
        "latency_reduction_vs_baseline_pct": "77.72",
    },
]


def project_root():
    return Path(__file__).resolve().parents[2]


def sleep(seconds, instant):
    if not instant:
        time.sleep(seconds)


def say(text="", instant=False, delay=0.7):
    print(text, flush=True)
    sleep(delay, instant)


def load_rows():
    csv_path = project_root() / "assets" / "mininet-policy-sweep" / "results" / "policy_comparison_table.csv"
    if not csv_path.exists():
        return FALLBACK_ROWS, csv_path, False

    rows = []
    with csv_path.open() as f:
        for row in csv.DictReader(f):
            if row["background_load_factor"] == "3" and row["queue_size_packets"] == "20":
                rows.append(row)
    if not rows:
        return FALLBACK_ROWS, csv_path, False
    return rows, csv_path, True


def as_float(row, key):
    return float(row[key])


def row_for(rows, policy):
    for row in rows:
        if row["policy"] == policy:
            return row
    raise KeyError(policy)


def print_header():
    print("=" * 78)
    print("UAV-EDGE KRITIK TRAFIK KORUMA DEMOSU")
    print("Bütünleme CLI anlatımı - doğrulanmış Mininet sonuçlarının tekrar oynatımı")
    print("=" * 78)


def print_table(rows):
    print()
    print("Sonuç tablosu: 3x background load, 10 Mbps darboğaz, 20 packet queue")
    print("-" * 96)
    print(f"{'Ilke':<24} {'Throughput':>12} {'RTT':>12} {'Loss':>10} {'Jitter':>12} {'Thr. gain':>12}")
    print(f"{'':<24} {'Mbps':>12} {'ms':>12} {'%':>10} {'ms':>12} {'%':>12}")
    print("-" * 96)
    for policy in ("baseline_fifo", "source_shaping", "switch_priority"):
        row = row_for(rows, policy)
        print(
            f"{POLICY_LABELS[policy]:<24} "
            f"{as_float(row, 'avg_throughput_mbps'):>12.3f} "
            f"{as_float(row, 'avg_latency_ms'):>12.3f} "
            f"{as_float(row, 'avg_packet_loss_pct'):>10.3f} "
            f"{as_float(row, 'avg_jitter_ms'):>12.3f} "
            f"{as_float(row, 'throughput_gain_vs_baseline_pct'):>12.2f}"
        )
    print("-" * 96)


def explain(rows, instant):
    baseline = row_for(rows, "baseline_fifo")
    source = row_for(rows, "source_shaping")
    switch = row_for(rows, "switch_priority")

    say("\n[1/6] Topoloji kuruluyor:", instant)
    say("      h1 -> h2 kritik TCP akışı, h3 -> h4 background UDP akışı.", instant)
    say("      s1 -> s2 linki ortak darboğaz: 10 Mbps, 20 ms delay, 20 packet queue.", instant)

    say("\n[2/6] En ağır tıkanıklık senaryosu seçiliyor:", instant)
    say("      Background load factor = 3x. Yani 10 Mbps linke 30 Mbps UDP yük bindiriliyor.", instant)

    say("\n[3/6] Baseline FIFO ilkesi okunuyor:", instant)
    say(
        f"      Kritik TCP throughput {as_float(baseline, 'avg_throughput_mbps'):.3f} Mbps, "
        f"RTT {as_float(baseline, 'avg_latency_ms'):.3f} ms, "
        f"packet loss %{as_float(baseline, 'avg_packet_loss_pct'):.3f}.",
        instant,
    )
    say("      Yorum: Kritik trafik background UDP ile aynı kuyrukta yarıştığı için bozuluyor.", instant)

    say("\n[4/6] Source shaping ilkesi okunuyor:", instant)
    say(
        f"      Throughput {as_float(source, 'avg_throughput_mbps'):.3f} Mbps, "
        f"RTT {as_float(source, 'avg_latency_ms'):.3f} ms, "
        f"loss %{as_float(source, 'avg_packet_loss_pct'):.3f}.",
        instant,
    )
    say("      Yorum: Background trafik kaynakta kısıldığı için kritik akış belirgin şekilde rahatlıyor.", instant)

    say("\n[5/6] Switch-side priority ilkesi okunuyor:", instant)
    say(
        f"      Throughput {as_float(switch, 'avg_throughput_mbps'):.3f} Mbps, "
        f"RTT {as_float(switch, 'avg_latency_ms'):.3f} ms, "
        f"jitter {as_float(switch, 'avg_jitter_ms'):.3f} ms.",
        instant,
    )
    say("      Yorum: Öncelik darboğaz switch çıkışında uygulandığı için SDN anlatısına daha yakın modeldir.", instant)

    say("\n[6/6] Sonuç cümlesi:", instant)
    say(
        f"      Switch-side priority, baseline'a göre throughput'u "
        f"%{as_float(switch, 'throughput_gain_vs_baseline_pct'):.2f} artırdı; "
        f"RTT gecikmesini %{as_float(switch, 'latency_reduction_vs_baseline_pct'):.2f} azalttı.",
        instant,
    )
    say(
        f"      Packet loss %{as_float(baseline, 'avg_packet_loss_pct'):.0f}'dan "
        f"%{as_float(switch, 'avg_packet_loss_pct'):.0f}'a indi.",
        instant,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instant", action="store_true", help="Bekleme yapmadan tüm anlatımı yazdır.")
    args = parser.parse_args()

    rows, csv_path, from_file = load_rows()
    print_header()
    if from_file:
        say(f"\nVeri kaynağı: {csv_path}", args.instant)
    else:
        say(f"\nUyarı: CSV bulunamadı veya eksik okundu. Gömülü doğrulanmış özet kullanılıyor: {csv_path}", args.instant)

    explain(rows, args.instant)
    print_table(rows)
    print("\nDemo tamamlandı. Sunumda bu tabloyu gösterip switch-side priority ilkesinin")
    print("kritik trafik için en düşük RTT/jitter ve sıfır packet loss verdiğini vurgulayabilirsin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
