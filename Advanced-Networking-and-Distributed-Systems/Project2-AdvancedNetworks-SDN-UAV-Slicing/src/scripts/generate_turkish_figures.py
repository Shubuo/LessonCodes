#!/usr/bin/env python3

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets" / "mininet_experiment"
SUMMARY = json.loads((OUT_DIR / "summary.json").read_text())
BANDWIDTHS = [5, 10, 20]

COLORS = {
    "navy": "#17324d",
    "blue": "#2f6feb",
    "cyan": "#5ec2d1",
    "muted": "#94a3b8",
    "soft": "#f5f7fb",
    "red": "#ef4444",
    "amber": "#f59e0b",
    "green": "#22c55e",
}


def load_repeats(metric):
    values = {"baseline": {}, "priority_slicing": {}}
    with (OUT_DIR / "measurements.csv").open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            policy = row["policy"]
            bw = int(row["bandwidth_mbps"])
            values[policy].setdefault(bw, []).append(float(row[metric]))
    return values


def style_axes(ax):
    ax.set_facecolor(COLORS["soft"])
    ax.grid(axis="y", color="#d8dee9", linewidth=1.1, alpha=0.7)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color("#667085")


def plot_metric(metric, ylabel, title, filename, color, ylim=None):
    x = np.arange(len(BANDWIDTHS))
    width = 0.34
    baseline = [SUMMARY[str(bw)]["baseline"][metric] for bw in BANDWIDTHS]
    priority = [SUMMARY[str(bw)]["priority_slicing"][metric] for bw in BANDWIDTHS]
    repeats = load_repeats(metric)
    baseline_std = [float(np.std(repeats["baseline"][bw])) for bw in BANDWIDTHS]
    priority_std = [float(np.std(repeats["priority_slicing"][bw])) for bw in BANDWIDTHS]

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=150)
    fig.patch.set_facecolor("white")
    style_axes(ax)

    bars1 = ax.bar(
        x - width / 2,
        baseline,
        width,
        yerr=baseline_std,
        capsize=5,
        label="Best-effort temel durum",
        color=COLORS["muted"],
        edgecolor="white",
        linewidth=1.2,
    )
    bars2 = ax.bar(
        x + width / 2,
        priority,
        width,
        yerr=priority_std,
        capsize=5,
        label="Öncelikli dilimleme",
        color=color,
        edgecolor="white",
        linewidth=1.2,
    )

    ax.set_title(title, fontsize=24, fontweight="bold", color=COLORS["navy"], pad=18)
    ax.set_xlabel("Darboğaz bant genişliği (Mbps)", fontsize=15, color=COLORS["navy"], labelpad=12)
    ax.set_ylabel(ylabel, fontsize=15, color=COLORS["navy"], labelpad=12)
    ax.set_xticks(x, [str(bw) for bw in BANDWIDTHS])
    ax.tick_params(axis="both", labelsize=12)
    if ylim:
        ax.set_ylim(ylim)

    legend = ax.legend(loc="upper left", frameon=True, fontsize=12)
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_edgecolor("#d8dee9")

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            label = f"{height:.2f}"
            ax.annotate(
                label,
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=11,
                color=COLORS["navy"],
                fontweight="bold",
            )

    fig.text(
        0.065,
        0.035,
        "Kaynak: Mininet üzerinde 3 tekrarın ortalaması; hata çubukları standart sapmayı gösterir.",
        fontsize=10,
        color="#667085",
    )
    fig.tight_layout(rect=[0.035, 0.055, 0.985, 0.965])
    fig.savefig(OUT_DIR / filename)
    plt.close(fig)


def plot_topology():
    graph = nx.Graph()
    graph.add_edges_from([
        ("h1\nİHA\nKritik TCP", "s1\nOVS kenar"),
        ("h3\nArka plan\nUDP yük", "s1\nOVS kenar"),
        ("s1\nOVS kenar", "s2\nDarboğaz\nswitch"),
        ("s2\nDarboğaz\nswitch", "h2\nEdge sunucu"),
        ("s2\nDarboğaz\nswitch", "h4\nCloud /\narka plan"),
    ])
    pos = {
        "h1\nİHA\nKritik TCP": (-2.1, 1.0),
        "h3\nArka plan\nUDP yük": (-2.1, -1.0),
        "s1\nOVS kenar": (-0.65, 0),
        "s2\nDarboğaz\nswitch": (0.75, 0),
        "h2\nEdge sunucu": (2.1, 1.0),
        "h4\nCloud /\narka plan": (2.1, -1.0),
    }
    node_colors = [COLORS["cyan"], COLORS["blue"], COLORS["muted"], COLORS["blue"], COLORS["green"], COLORS["amber"]]

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    nx.draw_networkx_edges(graph, pos, width=3.2, edge_color="#475569", ax=ax)
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_size=4300,
        node_color=node_colors,
        edgecolors="white",
        linewidths=2.4,
        ax=ax,
    )
    nx.draw_networkx_labels(graph, pos, font_size=12, font_weight="bold", font_color=COLORS["navy"], ax=ax)

    ax.text(-0.05, 0.18, "TCLink\n20 ms, 20 pkt", ha="center", va="center", fontsize=10, color="#667085")
    ax.set_title("Mininet İHA-Edge Deney Topolojisi", fontsize=24, fontweight="bold", color=COLORS["navy"], pad=18)
    ax.axis("off")
    fig.tight_layout(rect=[0.02, 0.02, 0.98, 0.96])
    fig.savefig(OUT_DIR / "topology_graph.png")
    plt.close(fig)


def main():
    plot_topology()
    plot_metric(
        "throughput_mbps",
        "Kritik TCP veri hızı (Mbps)",
        "Veri Hızı (Throughput) Değerlendirmesi",
        "throughput_results.png",
        COLORS["blue"],
        (0, 9.5),
    )
    plot_metric(
        "latency_ms",
        "Ortalama RTT gecikmesi (ms)",
        "Gecikme Değerlendirmesi",
        "latency_results.png",
        COLORS["cyan"],
        (0, 145),
    )
    plot_metric(
        "packet_loss_pct",
        "ICMP paket kaybı (%)",
        "Paket Kaybı Değerlendirmesi",
        "packet_loss_results.png",
        COLORS["red"],
        (0, 22),
    )
    plot_metric(
        "jitter_ms",
        "RTT mdev / jitter göstergesi (ms)",
        "Gecikme Dalgalanması (Jitter)",
        "jitter_results.png",
        COLORS["amber"],
        (0, 55),
    )


if __name__ == "__main__":
    main()
