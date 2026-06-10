#!/usr/bin/env python3

import csv
import json
import os
import re
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSController


OUT_DIR = Path("/home/ubuntu/mininet-uav-exp/results")
RAW_DIR = OUT_DIR / "raw"
BANDWIDTHS = [5, 10, 20]
POLICIES = ["baseline", "priority_slicing"]
REPEATS = 3
DELAY_MS = 20
QUEUE_SIZE = 20


def ensure_dirs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def run_cmd(node, command):
    return node.cmd(command)


def parse_iperf_mbps(output):
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


def create_network(bw_mbps, policy):
    net = Mininet(controller=OVSController, link=TCLink, autoSetMacs=True)
    net.addController("c0", controller=OVSController)

    h1 = net.addHost("h1", ip="10.0.0.1/24")  # UAV / critical source
    h2 = net.addHost("h2", ip="10.0.0.2/24")  # Edge server
    h3 = net.addHost("h3", ip="10.0.0.3/24")  # Background source
    h4 = net.addHost("h4", ip="10.0.0.4/24")  # Background sink / cloud
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")

    net.addLink(h1, s1, bw=100, delay="1ms", max_queue_size=1000, use_htb=True)
    net.addLink(h3, s1, bw=100, delay="1ms", max_queue_size=1000, use_htb=True)
    net.addLink(s2, h2, bw=100, delay="1ms", max_queue_size=1000, use_htb=True)
    net.addLink(s2, h4, bw=100, delay="1ms", max_queue_size=1000, use_htb=True)

    # Shared bottleneck link: both critical and background flows traverse this link.
    net.addLink(
        s1,
        s2,
        bw=bw_mbps,
        delay=f"{DELAY_MS}ms",
        max_queue_size=QUEUE_SIZE,
        use_htb=True,
    )

    net.start()

    if policy == "priority_slicing":
        # Emulate an SDN slicing policy by policing non-critical traffic at the edge.
        # The critical UAV flow is not capped; background traffic is limited to 20%.
        bg_cap = max(1, int(round(bw_mbps * 0.2)))
        h3.cmd("tc qdisc del dev h3-eth0 root 2>/dev/null || true")
        h3.cmd(
            f"tc qdisc add dev h3-eth0 root tbf rate {bg_cap}mbit "
            "burst 32kbit latency 50ms"
        )

    return net


def stop_processes(net):
    for host in net.hosts:
        host.cmd("killall -9 iperf 2>/dev/null || true")
        host.cmd("tc qdisc del dev %s-eth0 root 2>/dev/null || true" % host.name)


def run_trial(bw_mbps, policy, repeat):
    net = create_network(bw_mbps, policy)
    h1, h2, h3, h4 = [net.get(name) for name in ("h1", "h2", "h3", "h4")]

    try:
        net.pingAll(timeout="1")

        h2.cmd("iperf -s -p 5001 -w 512K > /tmp/iperf_critical_server.log 2>&1 &")
        h4.cmd("iperf -s -u -p 5002 > /tmp/iperf_background_server.log 2>&1 &")
        time.sleep(0.7)

        offered_rate = max(2, bw_mbps * 2)
        bg_cmd = (
            f"timeout 20 iperf -u -c 10.0.0.4 -p 5002 -b {offered_rate}M "
            "-t 18 -i 1 > /tmp/iperf_background_client.log 2>&1"
        )
        bg_proc = h3.popen(bg_cmd, shell=True)
        time.sleep(1.0)

        critical_output = run_cmd(
            h1,
            "timeout 14 iperf -c 10.0.0.2 -p 5001 -w 512K -t 8 -i 1 2>&1",
        )
        ping_output = run_cmd(
            h1,
            "timeout 8 ping -c 20 -i 0.2 10.0.0.2 2>&1",
        )

        bg_proc.wait(timeout=20)
        background_output = h3.cmd("cat /tmp/iperf_background_client.log 2>/dev/null || true")
        critical_server = h2.cmd("cat /tmp/iperf_critical_server.log 2>/dev/null || true")
        background_server = h4.cmd("cat /tmp/iperf_background_server.log 2>/dev/null || true")

        throughput = parse_iperf_mbps(critical_output)
        latency, loss, jitter = parse_ping(ping_output)

        prefix = f"bw{bw_mbps}_{policy}_r{repeat}"
        (RAW_DIR / f"{prefix}_critical_client.log").write_text(critical_output)
        (RAW_DIR / f"{prefix}_critical_server.log").write_text(critical_server)
        (RAW_DIR / f"{prefix}_ping.log").write_text(ping_output)
        (RAW_DIR / f"{prefix}_background_client.log").write_text(background_output)
        (RAW_DIR / f"{prefix}_background_server.log").write_text(background_server)

        return {
            "bandwidth_mbps": bw_mbps,
            "policy": policy,
            "repeat": repeat,
            "throughput_mbps": round(throughput, 3),
            "latency_ms": round(latency, 3),
            "packet_loss_pct": round(loss, 3),
            "jitter_ms": round(jitter, 3),
            "background_offered_mbps": offered_rate,
            "delay_ms": DELAY_MS,
            "queue_size_packets": QUEUE_SIZE,
        }
    finally:
        stop_processes(net)
        net.stop()


def write_csv(rows):
    path = OUT_DIR / "measurements.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows):
    summary = {}
    for bw in BANDWIDTHS:
        summary[str(bw)] = {}
        for policy in POLICIES:
            subset = [r for r in rows if r["bandwidth_mbps"] == bw and r["policy"] == policy]
            summary[str(bw)][policy] = {
                "throughput_mbps": round(float(np.mean([r["throughput_mbps"] for r in subset])), 3),
                "latency_ms": round(float(np.mean([r["latency_ms"] for r in subset])), 3),
                "packet_loss_pct": round(float(np.mean([r["packet_loss_pct"] for r in subset])), 3),
                "jitter_ms": round(float(np.mean([r["jitter_ms"] for r in subset])), 3),
            }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def plot_metric(summary, metric, ylabel, title, filename, color):
    x = np.arange(len(BANDWIDTHS))
    width = 0.35
    baseline = [summary[str(bw)]["baseline"][metric] for bw in BANDWIDTHS]
    priority = [summary[str(bw)]["priority_slicing"][metric] for bw in BANDWIDTHS]

    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=120)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#f5f7fb")
    ax.bar(x - width / 2, baseline, width, label="Best-effort baseline", color="#94a3b8")
    ax.bar(x + width / 2, priority, width, label="Priority slicing", color=color)
    ax.set_title(title, fontsize=20, fontweight="bold", color="#17324d", pad=18)
    ax.set_xlabel("Bottleneck bandwidth (Mbps)", fontsize=13)
    ax.set_ylabel(ylabel, fontsize=13)
    ax.set_xticks(x, [str(bw) for bw in BANDWIDTHS])
    ax.grid(axis="y", alpha=0.32)
    ax.legend(frameon=True)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=3, fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT_DIR / filename)
    plt.close(fig)


def plot_topology():
    graph = nx.Graph()
    graph.add_edges_from([
        ("h1\nUAV critical", "s1\nOVS edge"),
        ("h3\nbackground", "s1\nOVS edge"),
        ("s1\nOVS edge", "s2\nbottleneck switch"),
        ("s2\nbottleneck switch", "h2\nedge server"),
        ("s2\nbottleneck switch", "h4\ncloud/background sink"),
    ])
    pos = {
        "h1\nUAV critical": (-2, 1),
        "h3\nbackground": (-2, -1),
        "s1\nOVS edge": (-0.7, 0),
        "s2\nbottleneck switch": (0.9, 0),
        "h2\nedge server": (2.2, 1),
        "h4\ncloud/background sink": (2.2, -1),
    }
    colors = ["#5ec2d1", "#94a3b8", "#2f6feb", "#2f6feb", "#22c55e", "#f59e0b"]
    plt.figure(figsize=(12, 6.75), dpi=120)
    nx.draw_networkx_edges(graph, pos, width=3, edge_color="#475569")
    nx.draw_networkx_nodes(graph, pos, node_size=3600, node_color=colors, edgecolors="white", linewidths=2)
    nx.draw_networkx_labels(graph, pos, font_size=11, font_weight="bold", font_color="#17324d")
    plt.title("Mininet UAV-to-Edge Experiment Topology", fontsize=20, fontweight="bold", color="#17324d")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "topology_graph.png")
    plt.close()


def make_plots(summary):
    plot_topology()
    plot_metric(summary, "throughput_mbps", "Critical TCP throughput (Mbps)", "Throughput Evaluation", "throughput_results.png", "#2f6feb")
    plot_metric(summary, "latency_ms", "Average RTT latency (ms)", "Latency Evaluation", "latency_results.png", "#5ec2d1")
    plot_metric(summary, "packet_loss_pct", "ICMP packet loss (%)", "Packet Loss Evaluation", "packet_loss_results.png", "#ef4444")
    plot_metric(summary, "jitter_ms", "RTT mdev / jitter proxy (ms)", "Jitter Evaluation", "jitter_results.png", "#f59e0b")


def main():
    ensure_dirs()
    os.system("sudo mn -c >/dev/null 2>&1 || true")
    rows = []
    for bw in BANDWIDTHS:
        for policy in POLICIES:
            for repeat in range(1, REPEATS + 1):
                print(f"RUN bw={bw} policy={policy} repeat={repeat}", flush=True)
                rows.append(run_trial(bw, policy, repeat))
    write_csv(rows)
    summary = summarize(rows)
    make_plots(summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    setLogLevel("warning")
    main()
