#!/usr/bin/env python3
"""
Butunleme deneyi: UAV-Edge Mininet topolojisinde SDN slicing ilkelerini
karsilastiran otomatik policy sweep scripti.

Sunumda anlatilacak ana fikir:
1. h1 -> h2 arasindaki TCP akisi kritik UAV/edge trafigini temsil eder.
2. h3 -> h4 arasindaki UDP akisi background/cloud sync trafigini temsil eder.
3. s1 -> s2 linki ortak darbogazdir; iki trafik turu bu linkte yarismaktadir.
4. Bu script uc ilkeyi ayni kosullarda karsilastirir:
   - baseline_fifo: ozel onceliklendirme yok.
   - source_shaping: background trafik kaynakta kisitlanir.
   - switch_priority: darbogaz switch cikisinda kritik akis onceliklendirilir.

Kodun amaci tek bir demo kosusu yapmak degil; ayni senaryoyu farkli tikaniklik
seviyelerinde tekrar ederek rapora/sunuma girecek olculebilir kanit uretmektir.
"""

import argparse
import csv
import json
import os
import re
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSController


# Deney ciktilari VM icinde bu klasore yazilir. Sonradan `multipass transfer`
# ile lokal `Butunleme/assets/mininet-policy-sweep/results` altina cekilir.
OUT_DIR = Path("/home/ubuntu/mininet-uav-exp/policy_sweep")
RAW_DIR = OUT_DIR / "raw"

# Butunleme icin ana karsilastirma 10 Mbps darbogaz uzerinde yapildi. Onceki
# sunum 5/10/20 Mbps kapasite taramasi iceriyordu; burada yeni katkı olarak
# tikaniklik siddeti degistiriliyor.
BANDWIDTHS = [10]

# Background load factor, background UDP trafiginin darbogaz kapasitesinin kac
# kati hizda gonderilecegini belirtir. 3x, en agir tikaniklik kosuludur.
LOAD_FACTORS = [1, 2, 3]

# Hizli kosu sunuma yeten 27 deneyi uretir. --full verilirse queue size etkisini
# de gostermek icin 10/20/50 packet matrisi calistirilir.
FAST_QUEUE_SIZES = [20]
FULL_QUEUE_SIZES = [10, 20, 50]

# Uc ilke ayni topoloji, ayni trafik ve ayni olcum komutlariyla karsilastirilir.
POLICIES = ["baseline_fifo", "source_shaping", "switch_priority"]
REPEATS = 3
DELAY_MS = 20


def ensure_dirs():
    """Sonuc ve ham log klasorlerini olusturur."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def parse_iperf_mbps(output):
    """iperf TCP client ciktisindan son raporlanan throughput degerini Mbps'e cevirir."""
    matches = re.findall(r"([0-9]+(?:\.[0-9]+)?)\s+([KMG])bits/sec", output)
    if not matches:
        return 0.0
    value, unit = matches[-1]
    value = float(value)
    if unit == "K":
        return value / 1000.0
    if unit == "G":
        return value * 1000.0
    return value


def parse_ping(output):
    """ping ciktisindan ortalama RTT, packet loss ve mdev/jitter proxy degerini cikarir."""
    loss = 100.0
    avg = 0.0
    jitter = 0.0

    loss_match = re.search(r"([0-9]+(?:\.[0-9]+)?)% packet loss", output)
    if loss_match:
        loss = float(loss_match.group(1))

    rtt_match = re.search(
        r"(?:rtt|round-trip) min/avg/max/(?:mdev|stddev) = "
        r"([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+) ms",
        output,
    )
    if rtt_match:
        avg = float(rtt_match.group(2))
        jitter = float(rtt_match.group(4))

    return avg, loss, jitter


def apply_source_shaping(host, bw_mbps):
    """
    Final Sunumundaki yaklasimi temsil eden ilke.

    Burada background source olan h3 uzerine TBF (Token Bucket Filter) eklenir.
    Yani background trafik daha darbogaza girmeden kisitlanir. Bu pratikte
    kritik akisi korur; ancak SDN/switch-side kuyruk yonetimini tam gostermedigi
    icin butunlemede switch_priority ilkesini de ekledik.
    """
    background_rate = max(1, int(round(bw_mbps * 0.2)))
    host.cmd("tc qdisc del dev h3-eth0 root 2>/dev/null || true")
    host.cmd(
        f"tc qdisc add dev h3-eth0 root tbf rate {background_rate}mbit "
        "burst 32kbit latency 50ms"
    )


def apply_switch_priority(switch, iface, bw_mbps):
    """
    Butunleme icin eklenen ana iyilestirme.

    Bu ilke darbogaz cikisinda, yani s1 -> s2 arayuzunde HTB siniflari kurar:
    - 1:10 critical class: h1 kaynakli kritik UAV TCP akisi.
    - 1:20 background class: h3 kaynakli background UDP akisi.

    Kritik akis 80% minimum rate ve tam linke kadar ceil alabilir. Background
    akis 20% ile sinirlanir. Bu nedenle bu blok, "SDN switch seviyesinde QoS"
    fikrini source_shaping'e gore daha iyi temsil eder.
    """
    critical_rate = max(1, int(round(bw_mbps * 0.8)))
    background_rate = max(1, int(round(bw_mbps * 0.2)))

    # Once varsa eski qdisc temizlenir. Ayni VM'de ard arda deney kosarken
    # onceki policy kalintilari yeni kosuyu etkilemesin.
    switch.cmd(f"tc qdisc del dev {iface} root 2>/dev/null || true")

    # Root qdisc: HTB tabanli hiyerarsik kuyruk yapisi. Default class 20,
    # yani filtreye takilmayan trafik background sinifina duser.
    switch.cmd(f"tc qdisc add dev {iface} root handle 1: htb default 20")

    # Parent class fiziksel darbogaz kapasitesini temsil eder.
    switch.cmd(
        f"tc class add dev {iface} parent 1: classid 1:1 "
        f"htb rate {bw_mbps}mbit ceil {bw_mbps}mbit"
    )

    # Kritik akis sinifi: daha yuksek oncelik, yuksek garanti, link bos ise tam kapasite.
    switch.cmd(
        f"tc class add dev {iface} parent 1:1 classid 1:10 "
        f"htb rate {critical_rate}mbit ceil {bw_mbps}mbit prio 1"
    )

    # Background sinifi: dusuk oncelik ve 20% kapasite siniri.
    switch.cmd(
        f"tc class add dev {iface} parent 1:1 classid 1:20 "
        f"htb rate {background_rate}mbit ceil {background_rate}mbit prio 2"
    )

    # h1 kritik UAV kaynagi oldugu icin 1:10 sinifina yonlendirilir.
    switch.cmd(
        f"tc filter add dev {iface} protocol ip parent 1:0 prio 1 "
        "u32 match ip src 10.0.0.1/32 flowid 1:10"
    )

    # h3 background kaynak oldugu icin 1:20 sinifina yonlendirilir.
    switch.cmd(
        f"tc filter add dev {iface} protocol ip parent 1:0 prio 2 "
        "u32 match ip src 10.0.0.3/32 flowid 1:20"
    )


def create_network(bw_mbps, queue_size, policy):
    """
    Her deney tekrari icin temiz bir Mininet topolojisi kurar.

    Topoloji:
        h1 --> s1 == darbogaz == s2 --> h2
        h3 --> s1 == darbogaz == s2 --> h4

    h1 -> h2 kritik TCP akisidir.
    h3 -> h4 background UDP akisidir.
    s1 -> s2 ortak darbogaz linkidir.
    """
    net = Mininet(controller=OVSController, link=TCLink, autoSetMacs=True)
    net.addController("c0", controller=OVSController)

    # Host rolleri:
    # h1: UAV / critical source
    # h2: Edge server / critical sink
    # h3: Background sync source
    # h4: Cloud/background sink
    h1 = net.addHost("h1", ip="10.0.0.1/24")
    h2 = net.addHost("h2", ip="10.0.0.2/24")
    h3 = net.addHost("h3", ip="10.0.0.3/24")
    h4 = net.addHost("h4", ip="10.0.0.4/24")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")

    # Kenar linkleri genis tutulur; boylece olctugumuz problem bu linklerde degil,
    # yalnizca s1-s2 arasindaki ortak darbogazda ortaya cikar.
    net.addLink(h1, s1, bw=100, delay="1ms", max_queue_size=1000, use_htb=True)
    net.addLink(h3, s1, bw=100, delay="1ms", max_queue_size=1000, use_htb=True)
    net.addLink(s2, h2, bw=100, delay="1ms", max_queue_size=1000, use_htb=True)
    net.addLink(s2, h4, bw=100, delay="1ms", max_queue_size=1000, use_htb=True)

    # Deneyin ana darboğazi. Bandwidth, delay ve queue size burada kontrol edilir.
    bottleneck = net.addLink(
        s1,
        s2,
        bw=bw_mbps,
        delay=f"{DELAY_MS}ms",
        max_queue_size=queue_size,
        use_htb=True,
    )

    net.start()

    # Baseline icin ek ilke yoktur. Diger iki ilke ayni topoloji uzerine
    # deney baslamadan hemen once uygulanir.
    if policy == "source_shaping":
        apply_source_shaping(h3, bw_mbps)
    elif policy == "switch_priority":
        apply_switch_priority(s1, bottleneck.intf1.name, bw_mbps)

    return net, bottleneck.intf1.name


def stop_processes(net):
    """Her kosudan sonra iperf ve tc ayarlarini temizler."""
    for host in net.hosts:
        host.cmd("killall -9 iperf 2>/dev/null || true")
        host.cmd(f"tc qdisc del dev {host.name}-eth0 root 2>/dev/null || true")
    for switch in net.switches:
        for intf in switch.intfList():
            if intf.name != "lo":
                switch.cmd(f"tc qdisc del dev {intf.name} root 2>/dev/null || true")


def run_trial(bw_mbps, load_factor, queue_size, policy, repeat):
    """
    Tek bir deney kosusunu calistirir ve olcum satiri dondurur.

    Parametreler dosya adina da yazilir. Bu sayede ham loglarda hangi kosunun
    hangi policy/load/queue/repeat kombinasyonuna ait oldugu kolayca izlenir.
    """
    net, bottleneck_iface = create_network(bw_mbps, queue_size, policy)
    h1, h2, h3, h4 = [net.get(name) for name in ("h1", "h2", "h3", "h4")]

    try:
        # Basit connectivity kontrolu. Bu adim topoloji kurulmus mu ve IP'ler
        # birbirini goruyor mu sorusuna hizli cevap verir.
        net.pingAll(timeout="1")

        # h2 kritik TCP server, h4 background UDP server olarak calisir.
        # Loglar /tmp altina yazilir; kosu sonunda RAW_DIR altina kopyalanir.
        h2.cmd("iperf -s -p 5001 -w 512K > /tmp/iperf_critical_server.log 2>&1 &")
        h4.cmd("iperf -s -u -p 5002 > /tmp/iperf_background_server.log 2>&1 &")
        time.sleep(0.7)

        # Background offered load, darbogaz kapasitesinin load_factor kati.
        # Ornek: 10 Mbps darbogaz ve 3x load => 30 Mbps UDP background denemesi.
        offered_rate = max(1, int(round(bw_mbps * load_factor)))
        bg_cmd = (
            f"timeout 20 iperf -u -c 10.0.0.4 -p 5002 -b {offered_rate}M "
            "-t 18 -i 1 > /tmp/iperf_background_client.log 2>&1"
        )
        bg_proc = h3.popen(bg_cmd, shell=True)
        time.sleep(1.0)

        # Kritik TCP throughput ayni anda olculur. Background trafik calisirken
        # h1 -> h2 akisinin ne kadar kapasite alabildigi ana throughput metrigidir.
        critical_output = h1.cmd(
            "timeout 14 iperf -c 10.0.0.2 -p 5001 -w 512K -t 8 -i 1 2>&1"
        )

        # RTT, packet loss ve jitter proxy icin ping kullanilir. ping mdev degeri
        # tam RTP jitter olcumu degildir; ama gecikme dalgalanmasi icin pratik proxy'dir.
        ping_output = h1.cmd("timeout 8 ping -c 20 -i 0.2 10.0.0.2 2>&1")

        bg_proc.wait(timeout=20)
        background_output = h3.cmd("cat /tmp/iperf_background_client.log 2>/dev/null || true")
        critical_server = h2.cmd("cat /tmp/iperf_critical_server.log 2>/dev/null || true")
        background_server = h4.cmd("cat /tmp/iperf_background_server.log 2>/dev/null || true")

        throughput = parse_iperf_mbps(critical_output)
        latency, loss, jitter = parse_ping(ping_output)

        # Her kosuya ait bes ham log saklanir:
        # critical client/server, ping, background client/server.
        prefix = f"bw{bw_mbps}_load{load_factor}_q{queue_size}_{policy}_r{repeat}"
        (RAW_DIR / f"{prefix}_critical_client.log").write_text(critical_output)
        (RAW_DIR / f"{prefix}_critical_server.log").write_text(critical_server)
        (RAW_DIR / f"{prefix}_ping.log").write_text(ping_output)
        (RAW_DIR / f"{prefix}_background_client.log").write_text(background_output)
        (RAW_DIR / f"{prefix}_background_server.log").write_text(background_server)

        return {
            "bandwidth_mbps": bw_mbps,
            "background_load_factor": load_factor,
            "queue_size_packets": queue_size,
            "policy": policy,
            "repeat": repeat,
            "throughput_mbps": round(throughput, 3),
            "latency_ms": round(latency, 3),
            "packet_loss_pct": round(loss, 3),
            "jitter_ms": round(jitter, 3),
            "background_offered_mbps": offered_rate,
            "delay_ms": DELAY_MS,
            "bottleneck_iface": bottleneck_iface,
        }
    finally:
        # Hata olsa bile Mininet ve tc state temizlenir. Aksi halde sonraki kosu
        # eski qdisc/iperf sureclerinden etkilenebilir.
        stop_processes(net)
        net.stop()


def write_csv(rows):
    """Tum deney satirlarini tek CSV dosyasina yazar."""
    path = OUT_DIR / "measurements.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def mean_metric(rows, metric):
    """Ayni konfigurasyonun tekrarlarini ortalamak icin yardimci fonksiyon."""
    return round(float(np.mean([r[metric] for r in rows])), 3)


def summarize(rows):
    """
    CSV'den daha kolay okunabilir JSON ozet uretir.

    Hiyerarsi:
        bandwidth -> load_factor -> queue_size -> policy -> metrics
    """
    summary = {}
    for bw in sorted({r["bandwidth_mbps"] for r in rows}):
        summary[str(bw)] = {}
        for load in sorted({r["background_load_factor"] for r in rows}):
            summary[str(bw)][str(load)] = {}
            for queue in sorted({r["queue_size_packets"] for r in rows}):
                summary[str(bw)][str(load)][str(queue)] = {}
                for policy in POLICIES:
                    subset = [
                        r for r in rows
                        if r["bandwidth_mbps"] == bw
                        and r["background_load_factor"] == load
                        and r["queue_size_packets"] == queue
                        and r["policy"] == policy
                    ]
                    if not subset:
                        continue
                    summary[str(bw)][str(load)][str(queue)][policy] = {
                        "throughput_mbps": mean_metric(subset, "throughput_mbps"),
                        "latency_ms": mean_metric(subset, "latency_ms"),
                        "packet_loss_pct": mean_metric(subset, "packet_loss_pct"),
                        "jitter_ms": mean_metric(subset, "jitter_ms"),
                    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def plot_quick_overview(rows):
    """
    VM icinde hizli kontrol grafigi uretir.

    Daha detayli ve sunuma uygun grafikler `analyze_policy_sweep.py` ile
    sonradan uretilir. Bu grafik, deney biter bitmez sonuclar makul mu diye
    bakmak icin kullanilir.
    """
    queue = sorted({r["queue_size_packets"] for r in rows})[0]
    loads = sorted({r["background_load_factor"] for r in rows})
    policies = POLICIES
    colors = {
        "baseline_fifo": "#94a3b8",
        "source_shaping": "#38bdf8",
        "switch_priority": "#2f6feb",
    }

    fig, axes = plt.subplots(2, 2, figsize=(12, 7), dpi=120)
    fig.patch.set_facecolor("white")
    metrics = [
        ("throughput_mbps", "Critical throughput (Mbps)"),
        ("latency_ms", "RTT latency (ms)"),
        ("packet_loss_pct", "Packet loss (%)"),
        ("jitter_ms", "Jitter proxy / mdev (ms)"),
    ]

    for ax, (metric, ylabel) in zip(axes.ravel(), metrics):
        for policy in policies:
            values = []
            for load in loads:
                subset = [
                    r for r in rows
                    if r["background_load_factor"] == load
                    and r["queue_size_packets"] == queue
                    and r["policy"] == policy
                ]
                values.append(float(np.mean([r[metric] for r in subset])) if subset else 0.0)
            ax.plot(loads, values, marker="o", linewidth=2.2, label=policy, color=colors[policy])
        ax.set_xlabel("Background load factor")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.3)

    axes[0][0].legend(frameon=True, fontsize=8)
    fig.suptitle(f"Policy Sweep Overview (queue={queue} packets)", fontsize=16, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "policy_sweep_overview.png")
    plt.close(fig)


def main():
    """Deney matrisini secip tum kosulari sirayla calistiran ana fonksiyon."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Run the full queue-size matrix.")
    args = parser.parse_args()

    # Varsayilan: hizli ama savunulabilir butunleme kosusu (27 run).
    # --full: queue size etkisini de kapsayan daha uzun kosu (81 run).
    queue_sizes = FULL_QUEUE_SIZES if args.full else FAST_QUEUE_SIZES
    ensure_dirs()

    # Mininet onceki kosulardan kalan state'e hassastir; bu nedenle script basinda
    # `mn -c` ile kernel namespace/link kalintilari temizlenir.
    os.system("sudo mn -c >/dev/null 2>&1 || true")

    rows = []
    total = len(BANDWIDTHS) * len(LOAD_FACTORS) * len(queue_sizes) * len(POLICIES) * REPEATS
    current = 0
    for bw in BANDWIDTHS:
        for load_factor in LOAD_FACTORS:
            for queue_size in queue_sizes:
                for policy in POLICIES:
                    for repeat in range(1, REPEATS + 1):
                        current += 1
                        print(
                            f"RUN {current}/{total} bw={bw} load={load_factor} "
                            f"queue={queue_size} policy={policy} repeat={repeat}",
                            flush=True,
                        )
                        rows.append(run_trial(bw, load_factor, queue_size, policy, repeat))

    # Deney sonunda hem makine-okunur CSV/JSON hem de hizli gorsel ozet uretilir.
    write_csv(rows)
    summary = summarize(rows)
    plot_quick_overview(rows)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    setLogLevel("warning")
    main()
