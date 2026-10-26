"""Sunum 1 figürleri: NetworkX/matplotlib → figures/out/*.png.

Figürler slayta yaklaşık 1:1 ölçekte yerleştirilir; bu yüzden buradaki
punto değerleri projeksiyondaki punto değerleridir (PLAN.md: gövde ≥ 22 pt,
şekil içi etiket ≥ 18 pt).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.lines import Line2D

OUT = Path(__file__).parent / "out"

# metropolis-ege paleti + Okabe-Ito vermilyon (renk körü güvenli vurgu)
NAVY = "#17324d"
CYAN = "#5ec2d1"
TEXT = "#1d2430"
MUTED = "#667085"
EDGE = "#98a2b3"
ALERT = "#d55e00"

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 18,
    "axes.titlesize": 22,
    "text.color": TEXT,
    "savefig.dpi": 220,
    # Arial'da ₂ ve ∝ glifi yok → formüller mathtext ile
    "mathtext.fontset": "dejavusans",
})


def tr(x: float, digits: int = 2) -> str:
    """Türkçe ondalık ayırıcı: 0.26 → 0,26."""
    return f"{x:.{digits}f}".replace(".", ",")


def unit_disk_graph(pos: dict[int, tuple[float, float]], r: float) -> nx.Graph:
    """(i, j) ∈ E ⇔ ‖p_i − p_j‖ ≤ R."""
    g = nx.Graph()
    g.add_nodes_from(pos)
    for i in pos:
        for j in pos:
            if i < j and ((pos[i][0] - pos[j][0]) ** 2 + (pos[i][1] - pos[j][1]) ** 2) ** 0.5 <= r:
                g.add_edge(i, j)
    return g


def algebraic_connectivity(g: nx.Graph) -> float:
    """λ₂(L), L = D − A. Yalnız numpy: bu makinedeki conda scipy derlemesi yüklenemiyor."""
    a = nx.to_numpy_array(g)
    return float(np.linalg.eigvalsh(np.diag(a.sum(axis=1)) - a)[1])


def critical_uav_example() -> dict[str, float]:
    """Slayt 7: 12 İHA'lık sürüde röle İHA kesme düğümüdür; düşerse ağ bölünür."""
    R = 1.0
    pos = {
        # denetim kümesi (5 İHA, halka → kendi içinde 2-bağlantılı)
        1: (-0.30, 0.00), 2: (0.15, 0.60), 3: (0.15, -0.60), 4: (0.80, 0.35), 5: (0.80, -0.35),
        # röle İHA
        6: (1.50, 0.00),
        # yer istasyonu tarafı (6 İHA)
        7: (2.20, 0.35), 8: (2.20, -0.35), 9: (2.85, 0.60), 10: (2.85, -0.60), 11: (3.30, 0.00), 12: (2.90, 0.00),
    }
    relay = 6
    g = unit_disk_graph(pos, R)
    cut = set(nx.articulation_points(g))
    assert cut == {relay}, f"beklenen tek kesme düğümü {relay}, bulunan {cut}"

    bc = nx.betweenness_centrality(g, normalized=True)
    lam2_before = algebraic_connectivity(g)
    h = g.copy()
    h.remove_node(relay)
    comps = sorted(nx.connected_components(h), key=min)
    assert len(comps) == 2

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12.1, 4.5))
    sizes = {v: 650 + 3200 * bc[v] for v in g}

    # (a) bağlı sürü
    ax_a.add_patch(plt.Circle(pos[relay], R, fill=False, ls="--", lw=2, color=ALERT, alpha=0.6))
    nx.draw_networkx_edges(g, pos, ax=ax_a, width=2.8, edge_color=EDGE)
    normal = [v for v in g if v != relay]
    nx.draw_networkx_nodes(g, pos, nodelist=normal, ax=ax_a, node_color=NAVY,
                           node_size=[sizes[v] for v in normal], edgecolors="white", linewidths=2)
    nx.draw_networkx_nodes(g, pos, nodelist=[relay], ax=ax_a, node_color=ALERT, node_shape="D",
                           node_size=sizes[relay], edgecolors="white", linewidths=2)
    ax_a.annotate("R", xy=(pos[relay][0] + 0.71, pos[relay][1] + 0.71), fontsize=18, color=ALERT,
                  ha="left", va="bottom")
    ax_a.set_title(rf"(a) Bağlı sürü · $\lambda_2$ = {tr(lam2_before)}", loc="left", color=TEXT)

    # (b) röle düştükten sonra
    comp_color = {v: (NAVY if v in comps[0] else CYAN) for v in h}
    nx.draw_networkx_edges(h, pos, ax=ax_b, width=2.8, edge_color=EDGE)
    nx.draw_networkx_nodes(h, pos, nodelist=list(h), ax=ax_b, node_color=[comp_color[v] for v in h],
                           node_size=650, edgecolors=TEXT, linewidths=1.2)
    ax_b.scatter(*pos[relay], s=700, marker="X", color=MUTED, zorder=3)
    ax_b.set_title(r"(b) Röle İHA düştü · 2 bileşen · $\lambda_2$ = 0", loc="left", color=TEXT)

    for ax in (ax_a, ax_b):
        ax.set_aspect("equal")
        ax.set_xlim(-0.75, 3.75)
        ax.set_ylim(-1.05, 1.05)
        ax.axis("off")

    legend = [
        Line2D([], [], marker="D", ls="", color=ALERT, markersize=16, label="Kesme düğümü (cut vertex)"),
        Line2D([], [], marker="o", ls="", color=NAVY, markersize=16, label=r"Boyut $\propto$ arasındalık (betweenness)"),
        Line2D([], [], marker="X", ls="", color=MUTED, markersize=16, label="Düşen İHA"),
    ]
    fig.legend(handles=legend, loc="lower center", ncol=3, frameon=False, fontsize=18,
               bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "critical_uav_example.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return {"lambda2": lam2_before, "betweenness_relay": bc[relay],
            "components_after": len(comps), "largest_after": max(len(c) for c in comps)}


def save(fig, name: str):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def clean(ax, xlim, ylim):
    ax.set_aspect("equal")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")


def graph_snapshots():
    """Slayt 3: hareket bir bağlantıyı koparır, yenisini kurar; G(t) → G(t+Δt)."""
    R = 1.0
    pos_t = {1: (0.0, 0.0), 2: (0.8, 0.45), 3: (0.75, -0.5), 4: (1.6, 0.1), 5: (2.3, 0.6),
             6: (2.35, -0.4), 7: (3.1, 0.15), 8: (-0.6, 0.6), 9: (-0.7, -0.45), 10: (1.55, 0.95),
             11: (3.25, 1.0)}
    pos_n = dict(pos_t)
    pos_n[10] = (2.45, 1.15)   # yalnız 10 uçar: 2 ve 4 ile bağı kopar, 11 ile yeni bağ kurar
    g_t, g_n = unit_disk_graph(pos_t, R), unit_disk_graph(pos_n, R)
    lost = {tuple(sorted(e)) for e in g_t.edges} - {tuple(sorted(e)) for e in g_n.edges}
    new = {tuple(sorted(e)) for e in g_n.edges} - {tuple(sorted(e)) for e in g_t.edges}
    assert lost and new, (lost, new)

    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12.1, 3.75))
    ax_a.add_patch(plt.Circle(pos_t[4], R, fill=False, ls="--", lw=2, color=MUTED))
    ax_a.annotate("R", xy=(pos_t[4][0] + 0.72, pos_t[4][1] + 0.72), fontsize=20, color=MUTED)
    nx.draw_networkx_edges(g_t, pos_t, ax=ax_a, width=2.8, edge_color=EDGE)
    nx.draw_networkx_edges(g_t, pos_t, edgelist=list(lost), ax=ax_a, width=4, edge_color=ALERT)
    nx.draw_networkx_edges(g_n, pos_n, ax=ax_b, width=2.8, edge_color=EDGE)
    nx.draw_networkx_edges(g_n, pos_n, edgelist=list(new), ax=ax_b, width=4, edge_color=CYAN)
    for ax, pos in ((ax_a, pos_t), (ax_b, pos_n)):
        nx.draw_networkx_nodes(g_t, pos, ax=ax, node_color=NAVY, node_size=650, edgecolors="white", linewidths=2)
    ax_a.annotate("", xy=pos_n[10], xytext=pos_t[10],
                  arrowprops=dict(arrowstyle="-|>", lw=2.5, color=TEXT, mutation_scale=22, shrinkA=14, shrinkB=4))
    ax_a.set_title(r"$G(t)$", fontsize=24, color=TEXT)
    ax_b.set_title(r"$G(t+\Delta t)$", fontsize=24, color=TEXT)
    for ax in (ax_a, ax_b):
        clean(ax, (-1.0, 3.5), (-0.95, 1.4))
    legend = [Line2D([], [], color=ALERT, lw=5, label="Kopacak bağlantı"),
              Line2D([], [], color=CYAN, lw=5, label="Yeni bağlantı"),
              Line2D([], [], color=MUTED, lw=2, ls="--", label="İletişim menzili R")]
    fig.legend(handles=legend, loc="lower center", ncol=3, frameon=False, fontsize=18, bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    save(fig, "graph_snapshots.png")
    return {"lost": sorted(lost), "new": sorted(new)}


def architectures():
    """Slayt 5: merkezi / dağıtık / hiyerarşik; kritik düğümler vermilyon."""
    fig, axes = plt.subplots(1, 3, figsize=(12.1, 4.3))

    # merkezi: yer istasyonu (0) yıldızın merkezi
    star = nx.star_graph(7)
    pos = {0: (0, 0)} | {i: (np.cos(2 * np.pi * i / 7), np.sin(2 * np.pi * i / 7)) for i in range(1, 8)}
    nx.draw_networkx_edges(star, pos, ax=axes[0], width=2.8, edge_color=EDGE)
    nx.draw_networkx_nodes(star, pos, nodelist=range(1, 8), ax=axes[0], node_color=NAVY, node_size=520,
                           edgecolors="white", linewidths=2)
    nx.draw_networkx_nodes(star, pos, nodelist=[0], ax=axes[0], node_color=ALERT, node_shape="s", node_size=900,
                           edgecolors="white", linewidths=2)

    # dağıtık: birim disk grafı, kritik düğüm yok
    mesh_pos = {1: (-0.9, 0.5), 2: (-0.2, 0.85), 3: (0.6, 0.6), 4: (1.0, -0.1), 5: (0.35, -0.2),
                6: (-0.45, -0.1), 7: (-0.85, -0.75), 8: (0.0, -0.9), 9: (0.8, -0.85)}
    mesh = unit_disk_graph(mesh_pos, 0.95)
    assert not list(nx.articulation_points(mesh))
    nx.draw_networkx_edges(mesh, mesh_pos, ax=axes[1], width=2.8, edge_color=EDGE)
    nx.draw_networkx_nodes(mesh, mesh_pos, ax=axes[1], node_color=NAVY, node_size=520, edgecolors="white",
                           linewidths=2)

    # hiyerarşik: üç küme, küme başları (CH) omurga kurar
    h = nx.Graph()
    heads = {"a": (-0.6, 0.45), "b": (0.6, 0.45), "c": (0.0, -0.55)}
    h_pos = dict(heads)
    for ch, (x, y) in heads.items():
        for k, (dx, dy) in enumerate([(-0.38, 0.28), (0.0, 0.42), (0.38, 0.28)] if y > 0
                                     else [(-0.42, -0.2), (0.0, -0.4), (0.42, -0.2)]):
            m = f"{ch}{k}"
            h_pos[m] = (x + dx, y + dy)
            h.add_edge(ch, m)
    h.add_edges_from([("a", "b"), ("b", "c"), ("c", "a")])
    members = [v for v in h if v not in heads]
    nx.draw_networkx_edges(h, h_pos, edgelist=[e for e in h.edges if e[0] in heads and e[1] in heads],
                           ax=axes[2], width=4, edge_color=ALERT, alpha=0.7)
    nx.draw_networkx_edges(h, h_pos, edgelist=[e for e in h.edges if not (e[0] in heads and e[1] in heads)],
                           ax=axes[2], width=2.8, edge_color=EDGE)
    nx.draw_networkx_nodes(h, h_pos, nodelist=members, ax=axes[2], node_color=NAVY, node_size=520,
                           edgecolors="white", linewidths=2)
    nx.draw_networkx_nodes(h, h_pos, nodelist=list(heads), ax=axes[2], node_color=ALERT, node_shape="D",
                           node_size=760, edgecolors="white", linewidths=2)

    titles = ["Merkezi", "Dağıtık", "Hiyerarşik"]
    captions = ["Yer istasyonu =\ntek hata noktası", "Yerel bilgi, ölçeklenir;\nkritik düğüm yok",
                "Küme başları\nkritik omurga"]
    for ax, title, cap in zip(axes, titles, captions):
        clean(ax, (-1.35, 1.35), (-1.35, 1.35))
        ax.set_title(title, fontsize=24, fontweight="bold", color=NAVY)
        ax.text(0, -1.45, cap, ha="center", va="top", fontsize=19, color=TEXT)
    fig.tight_layout(w_pad=2)
    save(fig, "architectures.png")


METRICS = [
    ("Derece", r"$k_i=\sum_j a_{ij}$", "Kaç komşu? → yedeklilik", False),
    ("Kümelenme katsayısı", r"$C_i=\dfrac{2L_i}{k_i(k_i-1)}$", "Komşular da birbirine bağlı mı?", False),
    ("Ortalama yol uzunluğu", r"$\ell=\dfrac{1}{n(n-1)}\sum_{i\neq j} d_{ij}$", "Mesaj kaç sekmede ulaşır?", False),
    ("Arasındalık", r"$b(v)=\sum_{s\neq v\neq t}\dfrac{\sigma_{st}(v)}{\sigma_{st}}$", "Trafiği hangi İHA taşıyor?", True),
    ("Cebirsel bağlılık", r"$\lambda_2(L),\;\; L=D-A$", r"$\lambda_2>0 \;\Leftrightarrow\;$ ağ bağlı", True),
    ("Düğüm bağlılığı", r"$\kappa(G)$", r"$\kappa\geq 2$: tek arıza ağı bölmez", True),
]


def metric_cards():
    """Slayt 6: altı metrik; slayt 7'de kullanılanlar vermilyon şeritli."""
    fig = plt.figure(figsize=(12.1, 4.3))
    w, h, gap = 0.315, 0.44, 0.0275
    for idx, (name, formula, meaning, key) in enumerate(METRICS):
        col, row = idx % 3, idx // 3
        x0, y0 = col * (w + gap), 1 - (row + 1) * h - row * 0.12
        ax = fig.add_axes((x0, y0, w, h))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color="#f5f7fb", transform=ax.transAxes, clip_on=False))
        ax.add_patch(plt.Rectangle((0, 0.94), 1, 0.06, color=ALERT if key else NAVY, transform=ax.transAxes,
                                   clip_on=False))
        ax.text(0.05, 0.8, name, fontsize=20, fontweight="bold", color=NAVY, va="center")
        ax.text(0.05, 0.47, formula, fontsize=22, color=TEXT, va="center")
        ax.text(0.05, 0.12, meaning, fontsize=18, color=TEXT, va="center")
    save(fig, "metric_cards.png")


def p1_failure_tolerance():
    """Slayt 9: P1 Tablo 11 — arıza toleranslı algoritmalar, mimariye göre (bizim sayımız)."""
    arch = ["Merkezi", "Dağıtık", "Hibrit", "Hiyerarşik"]
    tolerant = np.array([0, 7, 0, 3])
    total = np.array([2, 15, 2, 9])
    fig, ax = plt.subplots(figsize=(5.9, 4.4))
    y = np.arange(len(arch))[::-1]
    ax.barh(y, tolerant, color=NAVY, height=0.6, label="Arıza toleranslı")
    ax.barh(y, total - tolerant, left=tolerant, color="#d8dee9", height=0.6, label="Değil / belirtilmemiş")
    for yi, t, n in zip(y, tolerant, total):
        ax.text(n + 0.3, yi, f"{t} / {n}", va="center", fontsize=20, color=TEXT, fontweight="bold")
    ax.set_yticks(y, arch, fontsize=20)
    ax.set_xlim(0, 18.5)
    ax.set_xlabel("Algoritma sayısı", fontsize=18, color=MUTED)
    ax.tick_params(axis="x", labelsize=16, colors=MUTED)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(EDGE)
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="lower center", bbox_to_anchor=(0.45, -0.38), ncol=2, frameon=False, fontsize=16,
              handlelength=1.2, columnspacing=1)
    save(fig, "p1_failure_tolerance.png")


def paper_figures(papers: Path):
    """Slayt 10–13: makale figürleri. Lisans: P2/P3 CC BY, P4 © IEEE (sınıf içi), P5 CC BY-NC-ND (kırpılmaz)."""
    import subprocess
    from tempfile import TemporaryDirectory

    from PIL import Image

    dest = OUT / "papers"
    dest.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory() as tmp:
        t = Path(tmp)
        subprocess.run(["pdftoppm", "-r", "600", "-f", "4", "-l", "4", "-png",
                        str(papers / "sensors-24-00011.pdf"), str(t / "p2")], check=True)
        # P2 Şekil 1: yalnız sağdaki iki katman (G_a, G_b) paneli — sol şema slayt boyutunda okunmuyor (CC BY)
        Image.open(next(t.glob("p2*.png"))).crop((2880, 1290, 4170, 2570)).save(dest / "p2_fig1.png")
        for name, pdf, page in [
            ("p3", "Dynamic_Topology_Organization_and_Maintenance_Algorithms_for_Autonomous_UAV_Swarms.pdf", 4),
            ("p4", "Graph_Attentional_Based_Agglomerative_Cluster_for_UAV_Swarm_Networks.pdf", 6),
            ("p5", "Distributed_biconnectivity-preserving_flocking_wit.pdf", 11),
        ]:
            subprocess.run(["pdfimages", "-j", "-f", str(page), "-l", str(page), str(papers / pdf),
                            str(t / name)], check=True)
        # P3 Şekil 1: yalnız üstteki yerleşim modeli paneli (CC BY uyarlamaya izin verir)
        Image.open(t / "p3-000.jpg").crop((0, 0, 1956, 1075)).save(dest / "p3_fig1_top.png")
        Image.open(t / "p4-000.jpg").save(dest / "p4_fig3.png")
        Image.open(t / "p5-000.jpg").save(dest / "p5_fig3.png")


PAPERS = Path("/Users/buraky/Library/CloudStorage/GoogleDrive-burakyoruk94@gmail.com/My Drive/"
              "2_ACADEMIA/PhD /2026-GUZ/Alg4ComplexNtw/papers")

if __name__ == "__main__":
    print("critical_uav_example:", critical_uav_example())
    print("graph_snapshots:", graph_snapshots())
    architectures()
    metric_cards()
    p1_failure_tolerance()
    paper_figures(PAPERS)
