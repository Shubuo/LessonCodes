#!/usr/bin/env python3

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


METRICS = [
    "throughput_mbps",
    "latency_ms",
    "packet_loss_pct",
    "jitter_ms",
]
POLICIES = ["baseline_fifo", "source_shaping", "switch_priority"]
POLICY_LABELS = {
    "baseline_fifo": "Baseline FIFO",
    "source_shaping": "Source shaping",
    "switch_priority": "Switch-side priority",
}
COLORS = {
    "baseline_fifo": "#94a3b8",
    "source_shaping": "#38bdf8",
    "switch_priority": "#2f6feb",
}


def read_rows(path):
    with Path(path).open() as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["bandwidth_mbps"] = int(float(row["bandwidth_mbps"]))
        row["background_load_factor"] = int(float(row["background_load_factor"]))
        row["queue_size_packets"] = int(float(row["queue_size_packets"]))
        row["repeat"] = int(float(row["repeat"]))
        for metric in METRICS:
            row[metric] = float(row[metric])
    return rows


def pct_reduction(baseline, value):
    if baseline == 0:
        return 0.0
    return round(((baseline - value) / baseline) * 100.0, 2)


def pct_gain(baseline, value):
    if baseline == 0:
        return 0.0
    return round(((value - baseline) / baseline) * 100.0, 2)


def aggregate(rows):
    grouped = defaultdict(list)
    for row in rows:
        key = (
            row["bandwidth_mbps"],
            row["background_load_factor"],
            row["queue_size_packets"],
            row["policy"],
        )
        grouped[key].append(row)

    aggregate_rows = []
    for key, values in sorted(grouped.items()):
        bw, load, queue, policy = key
        item = {
            "bandwidth_mbps": bw,
            "background_load_factor": load,
            "queue_size_packets": queue,
            "policy": policy,
        }
        for metric in METRICS:
            vals = [v[metric] for v in values]
            item[f"avg_{metric}"] = round(float(np.mean(vals)), 3)
            item[f"std_{metric}"] = round(float(np.std(vals)), 3)
        aggregate_rows.append(item)

    baseline_by_config = {
        (r["bandwidth_mbps"], r["background_load_factor"], r["queue_size_packets"]): r
        for r in aggregate_rows
        if r["policy"] == "baseline_fifo"
    }

    for row in aggregate_rows:
        baseline = baseline_by_config[
            (row["bandwidth_mbps"], row["background_load_factor"], row["queue_size_packets"])
        ]
        row["throughput_gain_vs_baseline_pct"] = pct_gain(
            baseline["avg_throughput_mbps"],
            row["avg_throughput_mbps"],
        )
        row["latency_reduction_vs_baseline_pct"] = pct_reduction(
            baseline["avg_latency_ms"],
            row["avg_latency_ms"],
        )
        row["loss_reduction_vs_baseline_pct"] = pct_reduction(
            baseline["avg_packet_loss_pct"],
            row["avg_packet_loss_pct"],
        )
        row["jitter_reduction_vs_baseline_pct"] = pct_reduction(
            baseline["avg_jitter_ms"],
            row["avg_jitter_ms"],
        )
    return aggregate_rows


def write_table(rows, output_dir):
    path = output_dir / "policy_comparison_table.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def choose_queue(rows):
    queues = sorted({r["queue_size_packets"] for r in rows})
    return 20 if 20 in queues else queues[0]


def metric_for(rows, load, queue, policy, metric):
    values = [
        r[f"avg_{metric}"] for r in rows
        if r["background_load_factor"] == load
        and r["queue_size_packets"] == queue
        and r["policy"] == policy
    ]
    return values[0] if values else 0.0


def plot_metric_lines(rows, output_dir, metric, ylabel, filename):
    queue = choose_queue(rows)
    loads = sorted({r["background_load_factor"] for r in rows if r["queue_size_packets"] == queue})
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=120)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#f5f7fb")

    for policy in POLICIES:
        vals = [metric_for(rows, load, queue, policy, metric) for load in loads]
        ax.plot(
            loads,
            vals,
            marker="o",
            linewidth=2.4,
            markersize=7,
            label=POLICY_LABELS[policy],
            color=COLORS[policy],
        )

    ax.set_title(ylabel + f" (queue={queue} packets)", fontsize=19, fontweight="bold", color="#17324d")
    ax.set_xlabel("Background load factor", fontsize=13)
    ax.set_ylabel(ylabel, fontsize=13)
    ax.set_xticks(loads)
    ax.grid(alpha=0.35)
    ax.legend(frameon=True)
    fig.tight_layout()
    fig.savefig(output_dir / filename)
    plt.close(fig)


def plot_improvement_bars(rows, output_dir):
    queue = choose_queue(rows)
    load = max(r["background_load_factor"] for r in rows if r["queue_size_packets"] == queue)
    selected = [
        r for r in rows
        if r["queue_size_packets"] == queue
        and r["background_load_factor"] == load
        and r["policy"] in ("source_shaping", "switch_priority")
    ]
    labels = [POLICY_LABELS[r["policy"]] for r in selected]
    throughput = [r["throughput_gain_vs_baseline_pct"] for r in selected]
    latency = [r["latency_reduction_vs_baseline_pct"] for r in selected]
    jitter = [r["jitter_reduction_vs_baseline_pct"] for r in selected]

    x = np.arange(len(labels))
    width = 0.25
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=120)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#f5f7fb")
    ax.bar(x - width, throughput, width, label="Throughput gain", color="#2f6feb")
    ax.bar(x, latency, width, label="Latency reduction", color="#5ec2d1")
    ax.bar(x + width, jitter, width, label="Jitter reduction", color="#f59e0b")
    ax.set_title(f"Improvement vs Baseline (load={load}x, queue={queue})", fontsize=19, fontweight="bold", color="#17324d")
    ax.set_ylabel("Improvement (%)")
    ax.set_xticks(x, labels)
    ax.grid(axis="y", alpha=0.35)
    ax.legend(frameon=True)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f", padding=3, fontsize=9)
    fig.tight_layout()
    fig.savefig(output_dir / "policy_improvement_vs_baseline.png")
    plt.close(fig)


def write_summary(rows, output_dir):
    queue = choose_queue(rows)
    load = max(r["background_load_factor"] for r in rows if r["queue_size_packets"] == queue)
    selected = [
        r for r in rows
        if r["queue_size_packets"] == queue
        and r["background_load_factor"] == load
    ]
    lines = [
        "# Policy Sweep Summary",
        "",
        f"Selected presentation slice: queue={queue} packets, background load={load}x.",
        "",
        "| Policy | Throughput Mbps | RTT ms | Loss % | Jitter ms | Throughput gain vs baseline % | Latency reduction vs baseline % |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for policy in POLICIES:
        row = next(r for r in selected if r["policy"] == policy)
        lines.append(
            f"| {POLICY_LABELS[policy]} | {row['avg_throughput_mbps']:.3f} | "
            f"{row['avg_latency_ms']:.3f} | {row['avg_packet_loss_pct']:.3f} | "
            f"{row['avg_jitter_ms']:.3f} | {row['throughput_gain_vs_baseline_pct']:.2f} | "
            f"{row['latency_reduction_vs_baseline_pct']:.2f} |"
        )
    (output_dir / "policy_sweep_summary.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = aggregate(read_rows(args.input))
    write_table(rows, output_dir)
    plot_metric_lines(rows, output_dir, "throughput_mbps", "Critical TCP throughput (Mbps)", "policy_throughput_results.png")
    plot_metric_lines(rows, output_dir, "latency_ms", "Average RTT latency (ms)", "policy_latency_results.png")
    plot_metric_lines(rows, output_dir, "packet_loss_pct", "Packet loss (%)", "policy_packet_loss_results.png")
    plot_metric_lines(rows, output_dir, "jitter_ms", "Jitter proxy / mdev (ms)", "policy_jitter_results.png")
    plot_improvement_bars(rows, output_dir)
    write_summary(rows, output_dir)
    print(f"Wrote policy sweep analysis to {output_dir}")


if __name__ == "__main__":
    main()
