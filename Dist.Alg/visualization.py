"""
Visualization and Graph Generation module for MDS Algorithm Project
Contains graph generation functions and all plotting functions
"""

from typing import List, Dict, Optional
import warnings
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import networkx as nx
import math
import os
import logging

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

logger = logging.getLogger(__name__)

# Results directory
RESULTS_DIR = "results"

# Constants (imported from main or defined here)
RANDOM_SEED = 42
MAX_GRAPH_SIZE_FOR_SIMULATION = 2000
DEFAULT_SNAP_FILE = "p2p-Gnutella04.txt"


# ==========================================
# GRAPH GENERATION FUNCTIONS
# ==========================================
# These helper functions create the network topologies used in the experiments.
#
# 1) generate_drone_network
#    - creates a Random Geometric Graph (RGG) using NetworkX,
#    - models a drone swarm where each drone has a limited communication range,
#    - places all nodes uniformly in a unit square and connects nodes that are
#      closer than a computed radio radius r,
#    - radius r is chosen such that the expected average degree is close to the
#      user‑specified avg_degree parameter:
#          r = sqrt( avg_degree / (pi * n) )
#      where n is the number of nodes.
#    - if the resulting graph is not connected, the largest connected component
#      is extracted so that both algorithms are evaluated on a single connected
#      network (fair comparison).
#
# 2) load_snap_dataset
#    - loads the real‑world P2P Gnutella graph from an edge‑list file,
#    - optionally trims the graph to MAX_GRAPH_SIZE_FOR_SIMULATION nodes in
#      order to keep simulation time reasonable,
#    - keeps only the largest connected component so that the algorithms do not
#      run on multiple disconnected islands,
#    - returns a NetworkX Graph object that can be directly passed to the
#      algorithm functions.

def generate_drone_network(n: int, avg_degree: float, seed: int = RANDOM_SEED, add_mobility: bool = False) -> nx.Graph:
    """
    Generate a Random Geometric Graph (RGG) representing a drone swarm.
    
    Parameters
    ----------
    n : int
        Number of nodes (drones) in the network.
    avg_degree : float
        Target average degree for nodes. Higher value means denser network.
    seed : int, optional
        Random seed for reproducibility.
    add_mobility : bool, optional
        If True, add speed and direction attributes to nodes for mobility-aware algorithms.
        Default is False.
        
    Returns
    -------
    nx.Graph
        A connected Random Geometric Graph. If the initially generated RGG is
        disconnected, only the largest connected component is returned and node
        labels are relabelled to be consecutive integers starting from 0.
        If add_mobility=True, nodes have 'speed' and 'direction' attributes.
    """
    if n <= 0:
        logger.warning("Number of nodes must be positive, returning empty graph")
        return nx.Graph()
    
    try:
        radius = math.sqrt(avg_degree / (math.pi * n))
        # NetworkX RGG creates nodes in a unit square
        G = nx.random_geometric_graph(n, radius, seed=seed)
        
        # Ensure connectivity for fair comparison (take largest component)
        if not nx.is_connected(G):
            largest_cc = max(nx.connected_components(G), key=len)
            G = G.subgraph(largest_cc).copy()
            # Relabel nodes to be continuous 0..k
            G = nx.convert_node_labels_to_integers(G)
        
        # Add mobility attributes if requested
        if add_mobility:
            try:
                np.random.seed(seed)
                for node_id in G.nodes():
                    # Speed: random between 0.1 and 2.0 (normalized units)
                    speed = np.random.uniform(0.1, 2.0)
                    # Direction: angle in radians (0 to 2*pi)
                    direction = np.random.uniform(0, 2 * math.pi)
                    G.nodes[node_id]['speed'] = speed
                    G.nodes[node_id]['direction'] = direction
            except Exception as e:
                logger.warning(f"Could not add mobility attributes: {e}. Continuing without mobility.")
        
        return G
    except Exception as e:
        logger.error(f"Error generating drone network: {e}")
        return nx.Graph()


def load_snap_dataset(filepath: str = DEFAULT_SNAP_FILE) -> Optional[nx.Graph]:
    """
    Load the SNAP P2P-Gnutella real-world dataset as a NetworkX Graph.
    
    The original dataset can be very large. To keep the simulation practical,
    this function:
      1) reads the graph from an edge‑list text file,
      2) if the graph has more than MAX_GRAPH_SIZE_FOR_SIMULATION nodes,
         takes an induced subgraph on the first MAX_GRAPH_SIZE_FOR_SIMULATION
         nodes,
      3) extracts the largest connected component to avoid running algorithms
         on multiple isolated components,
      4) relabels nodes to consecutive integers for cleaner output.
    
    Parameters
    ----------
    filepath : str, optional
        Path to the edge‑list file. By default uses DEFAULT_SNAP_FILE.
        
    Returns
    -------
    Optional[nx.Graph]
        A cleaned and connected NetworkX Graph object, or None if the file
        does not exist or loading fails.
    """
    if not os.path.exists(filepath):
        logger.warning(f"Dataset file '{filepath}' not found. Skipping Real-World test.")
        return None
    
    try:
        G = nx.read_edgelist(filepath, create_using=nx.Graph(), nodetype=int)
        
        # Simplify: Take a subgraph if too huge for simulation speed
        if len(G) > MAX_GRAPH_SIZE_FOR_SIMULATION:
            nodes = list(G.nodes())[:MAX_GRAPH_SIZE_FOR_SIMULATION]
            G = G.subgraph(nodes).copy()
            G = nx.convert_node_labels_to_integers(G)
        
        # Ensure connectivity
        if not nx.is_connected(G):
            largest_cc = max(nx.connected_components(G), key=len)
            G = G.subgraph(largest_cc).copy()
            G = nx.convert_node_labels_to_integers(G)
        
        return G
    except Exception as e:
        logger.error(f"Error loading SNAP dataset: {e}")
        return None


# ==========================================
# VISUALIZATION FUNCTIONS
# ==========================================


def plot_network_layout(G: nx.Graph, name: str, seq_mds: Optional[List[int]] = None, span_mds: Optional[List[int]] = None) -> None:
    """
    Plot the physical layout of a network with both Seq_11.1 and Span_11.2 MDS results side by side.

    This is especially useful for the Small_Swarm scenario, where we want to
    visually compare how the centralized (Seq) and distributed (Span) algorithms
    select dominating sets.

    Parameters
    ----------
    G : nx.Graph
        NetworkX graph to visualize. For RGG, node positions are expected to be
        stored in the 'pos' node attribute. If not present, a spring layout is
        used as a fallback.
    name : str
        Scenario name. Used only for file naming and title.
    seq_mds : list of int, optional
        MDS nodes from Seq_11.1 (centralized) algorithm.
    span_mds : list of int, optional
        MDS nodes from Span_11.2 (distributed) algorithm.
    """
    if G is None or len(G) == 0:
        logger.warning("plot_network_layout: empty graph, nothing to plot")
        return

    try:
        # Try to use existing RGG positions; otherwise fall back to spring_layout
        pos = nx.get_node_attributes(G, "pos")
        if not pos:
            pos = nx.spring_layout(G, seed=42)

        # Create figure with two subplots side by side
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
        fig.suptitle(f"Network Topology Comparison: {name}", fontsize=14, fontweight="bold")

        nodes = list(G.nodes())
        all_edges = list(G.edges())

        # LEFT SUBPLOT: Seq_11.1 (Centralized) Results
        seq_set = set(seq_mds) if seq_mds else set()
        # MDS edges: edges between MDS nodes
        seq_mds_edges = [e for e in all_edges if e[0] in seq_set and e[1] in seq_set]
        # Normal edges: all other edges
        seq_normal_edges = [e for e in all_edges if e not in seq_mds_edges]

        ax1.set_title(f"Seq_11.1 (Centralized)\nMDS Size: {len(seq_set)}", fontsize=11, fontweight="bold")
        
        # Draw edges: normal edges in light gray, MDS edges in thick black
        if seq_normal_edges:
            nx.draw_networkx_edges(G, pos, edgelist=seq_normal_edges, alpha=0.2, width=0.5, 
                                 edge_color="#CCCCCC", ax=ax1)
        if seq_mds_edges:
            nx.draw_networkx_edges(G, pos, edgelist=seq_mds_edges, alpha=1.0, width=3.0, 
                                 edge_color="#000000", ax=ax1)

        # Draw nodes: normal nodes in gray with white border, MDS nodes in black with white border
        if seq_set:
            seq_normal_nodes = [n for n in nodes if n not in seq_set]
            if seq_normal_nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=seq_normal_nodes, node_size=50, 
                                      node_color="#808080", edgecolors="#FFFFFF", linewidths=1.5,
                                      alpha=0.8, ax=ax1)
            # MDS nodes: black with white border, larger size
            nx.draw_networkx_nodes(G, pos, nodelist=list(seq_set), node_size=150, 
                                  node_color="#000000", edgecolors="#FFFFFF", linewidths=2.5,
                                  alpha=1.0, ax=ax1, label="MDS nodes")
        else:
            nx.draw_networkx_nodes(G, pos, node_size=50, node_color="#808080", 
                                  edgecolors="#FFFFFF", linewidths=1.5, alpha=0.8, ax=ax1)
        
        ax1.axis("off")

        # RIGHT SUBPLOT: Span_11.2 (Distributed) Results
        span_set = set(span_mds) if span_mds else set()
        # MDS edges: edges between MDS nodes
        span_mds_edges = [e for e in all_edges if e[0] in span_set and e[1] in span_set]
        # Normal edges: all other edges
        span_normal_edges = [e for e in all_edges if e not in span_mds_edges]

        ax2.set_title(f"Span_11.2 (Distributed)\nMDS Size: {len(span_set)}", fontsize=11, fontweight="bold")
        
        # Draw edges: normal edges in light gray, MDS edges in thick black
        if span_normal_edges:
            nx.draw_networkx_edges(G, pos, edgelist=span_normal_edges, alpha=0.2, width=0.5, 
                                 edge_color="#CCCCCC", ax=ax2)
        if span_mds_edges:
            nx.draw_networkx_edges(G, pos, edgelist=span_mds_edges, alpha=1.0, width=3.0, 
                                 edge_color="#000000", ax=ax2)

        # Draw nodes: normal nodes in gray with white border, MDS nodes in black with white border
        if span_set:
            span_normal_nodes = [n for n in nodes if n not in span_set]
            if span_normal_nodes:
                nx.draw_networkx_nodes(G, pos, nodelist=span_normal_nodes, node_size=50, 
                                      node_color="#808080", edgecolors="#FFFFFF", linewidths=1.5,
                                      alpha=0.8, ax=ax2)
            # MDS nodes: black with white border, larger size
            nx.draw_networkx_nodes(G, pos, nodelist=list(span_set), node_size=150, 
                                  node_color="#000000", edgecolors="#FFFFFF", linewidths=2.5,
                                  alpha=1.0, ax=ax2, label="MDS nodes")
        else:
            nx.draw_networkx_nodes(G, pos, node_size=50, node_color="#808080", 
                                  edgecolors="#FFFFFF", linewidths=1.5, alpha=0.8, ax=ax2)
        
        ax2.axis("off")

        # Save figure into results directory
        os.makedirs(RESULTS_DIR, exist_ok=True)
        safe_name = name.replace(" ", "_")
        filepath = os.path.join(RESULTS_DIR, f"topology_{safe_name}.png")
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        plt.close()
    except Exception as e:
        logger.error(f"Error while plotting network layout for {name}: {e}")
        import traceback

        logger.error(traceback.format_exc())


def plot_results(results: List[Dict]) -> None:
    """Creates visualization plots for the experiment results."""
    if not results:
        logger.warning("No results to plot.")
        return
    
    try:
        networks = [r['network'] for r in results]
        seq_sizes = [r['seq_size'] for r in results]
        span_sizes = [r['span_size'] for r in results]
        seq_times = [r['seq_time'] for r in results]
        span_times = [r['span_time'] for r in results]
        seq_msgs = [r['seq_msgs'] for r in results]
        span_msgs = [r['span_msgs'] for r in results]
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
        fig.suptitle('MDS Algorithm Performance Comparison: Seq_11.1 vs Span_11.2',
                     fontsize=14, fontweight='bold')
        
        x_pos = np.arange(len(networks))
        width = 0.35
        
        # 1. MDS Size Comparison
        ax1 = axes[0, 0]
        ax1.bar(x_pos - width/2, seq_sizes, width, label='Seq_11.1', color='#2E86AB', alpha=0.8)
        ax1.bar(x_pos + width/2, span_sizes, width, label='Span_11.2', color='#A23B72', alpha=0.8)
        ax1.set_xlabel('Network')
        ax1.set_ylabel('MDS Size')
        ax1.set_title('Dominating Set Size Comparison')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(networks, rotation=15, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Execution Time Comparison
        ax2 = axes[0, 1]
        ax2.bar(x_pos - width/2, seq_times, width, label='Seq_11.1', color='#2E86AB', alpha=0.8)
        ax2.bar(x_pos + width/2, span_times, width, label='Span_11.2', color='#A23B72', alpha=0.8)
        ax2.set_xlabel('Network')
        ax2.set_ylabel('Execution Time (seconds)')
        ax2.set_title('Execution Time Comparison')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(networks, rotation=15, ha='right')
        ax2.legend()
        if max(seq_times + span_times) / min([t for t in seq_times + span_times if t > 0]) > 10:
            ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Message Count Comparison
        ax3 = axes[1, 0]
        ax3.bar(x_pos - width/2, seq_msgs, width, label='Seq_11.1', color='#2E86AB', alpha=0.8)
        ax3.bar(x_pos + width/2, span_msgs, width, label='Span_11.2', color='#A23B72', alpha=0.8)
        ax3.set_xlabel('Network')
        ax3.set_ylabel('Message Count')
        ax3.set_title('Message Count Comparison')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(networks, rotation=15, ha='right')
        ax3.legend()
        if max(seq_msgs + span_msgs) > 0:
            max_msg = max(seq_msgs + span_msgs)
            min_msg = min([m for m in seq_msgs + span_msgs if m > 0])
            if max_msg / min_msg > 10:
                ax3.set_yscale('log')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Efficiency: Messages per Node
        ax4 = axes[1, 1]
        nodes = [r['num_nodes'] for r in results]
        seq_msgs_per_node = [msgs/n if n > 0 else 0 for msgs, n in zip(seq_msgs, nodes)]
        span_msgs_per_node = [msgs/n if n > 0 else 0 for msgs, n in zip(span_msgs, nodes)]
        ax4.bar(x_pos - width/2, seq_msgs_per_node, width, label='Seq_11.1', color='#2E86AB', alpha=0.8)
        ax4.bar(x_pos + width/2, span_msgs_per_node, width, label='Span_11.2', color='#A23B72', alpha=0.8)
        ax4.set_xlabel('Network')
        ax4.set_ylabel('Messages per Node')
        ax4.set_title('Communication Efficiency')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(networks, rotation=15, ha='right')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        
        os.makedirs(RESULTS_DIR, exist_ok=True)
        filepath = os.path.join(RESULTS_DIR, 'mds_performance_comparison.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        logger.error(f"Error creating plots: {e}")
        import traceback
        logger.error(traceback.format_exc())


def plot_algorithm_comparison(results: List[Dict]) -> None:
    """Creates detailed comparison visualization split into two halves."""
    if not results:
        return
    
    try:
        networks = [r['network'] for r in results]
        num_nodes = [r['num_nodes'] for r in results]
        seq_sizes = [r['seq_size'] for r in results]
        span_sizes = [r['span_size'] for r in results]
        seq_times = [r['seq_time'] for r in results]
        span_times = [r['span_time'] for r in results]
        span_msgs = [r['span_msgs'] for r in results]
        
        seq_efficiency = [s/n*100 if n > 0 else 0 for s, n in zip(seq_sizes, num_nodes)]
        span_efficiency = [s/n*100 if n > 0 else 0 for s, n in zip(span_sizes, num_nodes)]
        seq_speed = [n/t if t > 0 else 0 for n, t in zip(num_nodes, seq_times)]
        
        fig = plt.figure(figsize=(18, 10), constrained_layout=True)
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[1, 0])
        ax3 = fig.add_subplot(gs[0, 1])
        ax4 = fig.add_subplot(gs[1, 1])
        
        x_pos = np.arange(len(networks))
        width = 0.6
        
        # LEFT: Seq_11.1 Analysis
        ax1.bar(x_pos, seq_efficiency, width, color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax1.set_ylabel('MDS Coverage (%)', fontsize=11, fontweight='bold')
        ax1.set_title('Seq_11.1: MDS Coverage Efficiency\n(Küçük değer = Daha İyi)', 
                     fontsize=12, fontweight='bold', color='#2E86AB')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(networks, rotation=15, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')
        if len(seq_efficiency) > 0:
            mean_seq_eff = np.mean(seq_efficiency)
            ax1.axhline(y=mean_seq_eff, color='red', linestyle='--', 
                       linewidth=2, label=f'Ortalama: {mean_seq_eff:.2f}%')
        ax1.legend()
        for i, v in enumerate(seq_efficiency):
            ax1.text(i, v + 0.5, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax2.bar(x_pos, seq_speed, width, color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax2.set_ylabel('Processing Speed (nodes/sec)', fontsize=11, fontweight='bold')
        ax2.set_xlabel('Network', fontsize=11, fontweight='bold')
        ax2.set_title('Seq_11.1: Processing Speed\n(Yüksek değer = Daha Hızlı)', 
                     fontsize=12, fontweight='bold', color='#2E86AB')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(networks, rotation=15, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')
        if len(seq_speed) > 0:
            mean_seq_speed = np.mean(seq_speed)
            ax2.axhline(y=mean_seq_speed, color='red', linestyle='--', 
                       linewidth=2, label=f'Ortalama: {mean_seq_speed:.0f} nodes/s')
        ax2.legend()
        for i, v in enumerate(seq_speed):
            ax2.text(i, v + max(seq_speed)*0.02 if seq_speed else 0, f'{v:.0f}', ha='center', va='bottom', fontweight='bold')
        
        # RIGHT: Span_11.2 Analysis
        ax3.bar(x_pos, span_efficiency, width, color='#A23B72', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax3.set_ylabel('MDS Coverage (%)', fontsize=11, fontweight='bold')
        ax3.set_title('Span_11.2: MDS Coverage Efficiency\n(Küçük değer = Daha İyi)', 
                     fontsize=12, fontweight='bold', color='#A23B72')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(networks, rotation=15, ha='right')
        ax3.grid(True, alpha=0.3, axis='y')
        if len(span_efficiency) > 0:
            mean_span_eff = np.mean(span_efficiency)
            ax3.axhline(y=mean_span_eff, color='red', linestyle='--', 
                       linewidth=2, label=f'Ortalama: {mean_span_eff:.2f}%')
        ax3.legend()
        for i, v in enumerate(span_efficiency):
            ax3.text(i, v + 0.5, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        span_msgs_per_node = [m/n if n > 0 else 0 for m, n in zip(span_msgs, num_nodes)]
        ax4.bar(x_pos, span_msgs_per_node, width, color='#F18F01', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax4.set_ylabel('Messages per Node', fontsize=11, fontweight='bold')
        ax4.set_xlabel('Network', fontsize=11, fontweight='bold')
        ax4.set_title('Span_11.2: Communication Efficiency\n(Küçük değer = Daha Az Mesaj)', 
                     fontsize=12, fontweight='bold', color='#A23B72')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(networks, rotation=15, ha='right')
        ax4.grid(True, alpha=0.3, axis='y')
        if len(span_msgs_per_node) > 0:
            mean_span_msgs = np.mean(span_msgs_per_node)
            ax4.axhline(y=mean_span_msgs, color='red', linestyle='--', 
                       linewidth=2, label=f'Ortalama: {mean_span_msgs:.2f} msgs/node')
        ax4.legend()
        for i, v in enumerate(span_msgs_per_node):
            ax4.text(i, v + max(span_msgs_per_node)*0.02 if span_msgs_per_node else 0, f'{v:.1f}', ha='center', va='bottom', fontweight='bold')
        
        fig.suptitle('Algoritma Karşılaştırma Analizi: Seq_11.1 vs Span_11.2', 
                    fontsize=16, fontweight='bold')
        os.makedirs(RESULTS_DIR, exist_ok=True)
        filepath = os.path.join(RESULTS_DIR, 'algorithm_detailed_comparison.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        logger.error(f"Error creating detailed comparison: {e}")
        import traceback
        logger.error(traceback.format_exc())


def plot_performance_metrics(results: List[Dict]) -> None:
    """Creates normalized performance metrics comparison graph."""
    if not results:
        return
    
    try:
        networks = [r['network'] for r in results]
        num_nodes = [r['num_nodes'] for r in results]
        seq_sizes = [r['seq_size'] for r in results]
        span_sizes = [r['span_size'] for r in results]
        seq_times = [r['seq_time'] for r in results]
        span_times = [r['span_time'] for r in results]
        seq_msgs = [r['seq_msgs'] for r in results]
        span_msgs = [r['span_msgs'] for r in results]
        
        # Normalize metrics (0-1 scale, higher is better)
        max_size = max(seq_sizes + span_sizes)
        seq_size_score = [1 - (s / max_size) for s in seq_sizes]
        span_size_score = [1 - (s / max_size) for s in span_sizes]
        
        max_time = max(seq_times + span_times)
        seq_time_score = [1 - (t / max_time) if max_time > 0 else 1 for t in seq_times]
        span_time_score = [1 - (t / max_time) if max_time > 0 else 1 for t in span_times]
        
        max_msgs = max(seq_msgs + span_msgs) if max(seq_msgs + span_msgs) > 0 else 1
        seq_msg_score = [1 - (m / max_msgs) if max_msgs > 0 else 1 for m in seq_msgs]
        span_msg_score = [1 - (m / max_msgs) if max_msgs > 0 else 1 for m in span_msgs]
        
        seq_efficiency_score = [(1 - s/n) if n > 0 else 0 for s, n in zip(seq_sizes, num_nodes)]
        span_efficiency_score = [(1 - s/n) if n > 0 else 0 for s, n in zip(span_sizes, num_nodes)]
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12), constrained_layout=True)
        fig.suptitle('Normalize Edilmiş Performans Metrikleri Karşılaştırması\n(Yüksek Skor = Daha İyi)', 
                     fontsize=16, fontweight='bold')
        
        x_pos = np.arange(len(networks))
        width = 0.35
        
        # 1. MDS Küçüklüğü Skoru
        ax1 = axes[0, 0]
        bars1_1 = ax1.bar(x_pos - width/2, seq_size_score, width, label='Seq_11.1', 
                         color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars1_2 = ax1.bar(x_pos + width/2, span_size_score, width, label='Span_11.2', 
                         color='#A23B72', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax1.set_ylabel('Normalize Edilmiş Skor', fontsize=11, fontweight='bold')
        ax1.set_title('MDS Küçüklüğü Skoru\n(Küçük MDS = Yüksek Skor)', fontsize=12, fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(networks, rotation=15, ha='right', fontsize=9)
        ax1.set_ylim([0, 1.1])
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3, axis='y')
        for bars in [bars1_1, bars1_2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 2. Hız Skoru
        ax2 = axes[0, 1]
        bars2_1 = ax2.bar(x_pos - width/2, seq_time_score, width, label='Seq_11.1', 
                         color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars2_2 = ax2.bar(x_pos + width/2, span_time_score, width, label='Span_11.2', 
                         color='#A23B72', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax2.set_ylabel('Normalize Edilmiş Skor', fontsize=11, fontweight='bold')
        ax2.set_title('Hız Skoru\n(Hızlı = Yüksek Skor)', fontsize=12, fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(networks, rotation=15, ha='right', fontsize=9)
        ax2.set_ylim([0, 1.1])
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3, axis='y')
        for bars in [bars2_1, bars2_2]:
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 3. İletişim Verimliliği Skoru
        ax3 = axes[1, 0]
        bars3_1 = ax3.bar(x_pos - width/2, seq_msg_score, width, label='Seq_11.1', 
                         color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars3_2 = ax3.bar(x_pos + width/2, span_msg_score, width, label='Span_11.2', 
                         color='#A23B72', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax3.set_ylabel('Normalize Edilmiş Skor', fontsize=11, fontweight='bold')
        ax3.set_xlabel('Network', fontsize=11, fontweight='bold')
        ax3.set_title('İletişim Verimliliği Skoru\n(Az Mesaj = Yüksek Skor)', fontsize=12, fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(networks, rotation=15, ha='right', fontsize=9)
        ax3.set_ylim([0, 1.1])
        ax3.legend(loc='upper right')
        ax3.grid(True, alpha=0.3, axis='y')
        for bars in [bars3_1, bars3_2]:
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 4. Ağ Verimliliği Skoru
        ax4 = axes[1, 1]
        bars4_1 = ax4.bar(x_pos - width/2, seq_efficiency_score, width, label='Seq_11.1', 
                         color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars4_2 = ax4.bar(x_pos + width/2, span_efficiency_score, width, label='Span_11.2', 
                         color='#A23B72', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax4.set_ylabel('Normalize Edilmiş Skor', fontsize=11, fontweight='bold')
        ax4.set_xlabel('Network', fontsize=11, fontweight='bold')
        ax4.set_title('Ağ Verimliliği Skoru\n(Düşük MDS Oranı = Yüksek Skor)', fontsize=12, fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(networks, rotation=15, ha='right', fontsize=9)
        ax4.set_ylim([0, 1.1])
        ax4.legend(loc='upper right')
        ax4.grid(True, alpha=0.3, axis='y')
        for bars in [bars4_1, bars4_2]:
            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        os.makedirs(RESULTS_DIR, exist_ok=True)
        filepath = os.path.join(RESULTS_DIR, 'performance_metrics_comparison.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        logger.error(f"Error creating performance metrics comparison: {e}")
        import traceback
        logger.error(traceback.format_exc())


def plot_comprehensive_results(results: List[Dict]) -> None:
    """
    Creates a single comprehensive visualization with all key metrics.
    This replaces the 4 separate PNG files with one easy-to-analyze figure.
    """
    if not results:
        logger.warning("No results to plot.")
        return
    
    try:
        networks = [r['network'] for r in results]
        num_nodes = [r['num_nodes'] for r in results]
        seq_sizes = [r['seq_size'] for r in results]
        span_sizes = [r['span_size'] for r in results]
        seq_times = [r['seq_time'] for r in results]
        span_times = [r['span_time'] for r in results]
        seq_msgs = [r['seq_msgs'] for r in results]
        span_msgs = [r['span_msgs'] for r in results]
        
        # Mobility metrics (if available)
        topology_stability = [r.get('topology_stability', 0.0) for r in results]
        avg_edges = [r.get('avg_edges', 0.0) for r in results]
        avg_degree = [r.get('avg_degree', 0.0) for r in results]
        has_mobility = any(v > 0 for v in topology_stability)
        
        # Create a 2x3 or 3x3 grid depending on whether we have mobility metrics
        if has_mobility:
            fig, axes = plt.subplots(3, 3, figsize=(18, 18), constrained_layout=True)
        else:
            fig, axes = plt.subplots(2, 3, figsize=(18, 12), constrained_layout=True)
        fig.suptitle('Comprehensive MDS Algorithm Performance Analysis: Seq_11.1 vs Span_11.2',
                     fontsize=16, fontweight='bold')
        
        x_pos = np.arange(len(networks))
        width = 0.35
        
        # 1. MDS Size Comparison (Top Left)
        ax1 = axes[0, 0]
        bars1 = ax1.bar(x_pos - width/2, seq_sizes, width, label='Seq_11.1', color='#2E86AB', alpha=0.8)
        bars2 = ax1.bar(x_pos + width/2, span_sizes, width, label='Span_11.2', color='#A23B72', alpha=0.8)
        ax1.set_xlabel('Network', fontweight='bold')
        ax1.set_ylabel('MDS Size', fontweight='bold')
        ax1.set_title('1. Dominating Set Size\n(Lower is Better)', fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(networks, rotation=15, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        # 2. Execution Time Comparison (Top Middle)
        ax2 = axes[0, 1]
        bars3 = ax2.bar(x_pos - width/2, seq_times, width, label='Seq_11.1', color='#2E86AB', alpha=0.8)
        bars4 = ax2.bar(x_pos + width/2, span_times, width, label='Span_11.2', color='#A23B72', alpha=0.8)
        ax2.set_xlabel('Network', fontweight='bold')
        ax2.set_ylabel('Execution Time (seconds)', fontweight='bold')
        ax2.set_title('2. Execution Time\n(Lower is Better)', fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(networks, rotation=15, ha='right')
        ax2.legend()
        if max(seq_times + span_times) / min([t for t in seq_times + span_times if t > 0]) > 10:
            ax2.set_yscale('log')
        ax2.grid(True, alpha=0.3, axis='y')
        # Add value labels
        for bars in [bars3, bars4]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.4f}s', ha='center', va='bottom', fontsize=8, rotation=90)
        
        # 3. Message Count Comparison (Top Right)
        ax3 = axes[0, 2]
        bars5 = ax3.bar(x_pos - width/2, seq_msgs, width, label='Seq_11.1', color='#2E86AB', alpha=0.8)
        bars6 = ax3.bar(x_pos + width/2, span_msgs, width, label='Span_11.2', color='#A23B72', alpha=0.8)
        ax3.set_xlabel('Network', fontweight='bold')
        ax3.set_ylabel('Total Messages', fontweight='bold')
        ax3.set_title('3. Communication Overhead\n(Lower is Better)', fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(networks, rotation=15, ha='right')
        ax3.legend()
        if max(seq_msgs + span_msgs) > 0:
            max_msg = max(seq_msgs + span_msgs)
            min_msg = min([m for m in seq_msgs + span_msgs if m > 0])
            if max_msg / min_msg > 10:
                ax3.set_yscale('log')
        ax3.grid(True, alpha=0.3, axis='y')
        # Add value labels
        for bars in [bars5, bars6]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax3.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}', ha='center', va='bottom', fontsize=8)
        
        # 4. Messages per Node (Bottom Left)
        ax4 = axes[1, 0]
        seq_msgs_per_node = [msgs/n if n > 0 else 0 for msgs, n in zip(seq_msgs, num_nodes)]
        span_msgs_per_node = [msgs/n if n > 0 else 0 for msgs, n in zip(span_msgs, num_nodes)]
        bars7 = ax4.bar(x_pos - width/2, seq_msgs_per_node, width, label='Seq_11.1', color='#2E86AB', alpha=0.8)
        bars8 = ax4.bar(x_pos + width/2, span_msgs_per_node, width, label='Span_11.2', color='#A23B72', alpha=0.8)
        ax4.set_xlabel('Network', fontweight='bold')
        ax4.set_ylabel('Messages per Node', fontweight='bold')
        ax4.set_title('4. Communication Efficiency\n(Lower is Better)', fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(networks, rotation=15, ha='right')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')
        # Add value labels
        for bars in [bars7, bars8]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax4.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        # 5. MDS Coverage Ratio (Bottom Middle)
        ax5 = axes[1, 1]
        seq_coverage = [s/n*100 if n > 0 else 0 for s, n in zip(seq_sizes, num_nodes)]
        span_coverage = [s/n*100 if n > 0 else 0 for s, n in zip(span_sizes, num_nodes)]
        bars9 = ax5.bar(x_pos - width/2, seq_coverage, width, label='Seq_11.1', color='#2E86AB', alpha=0.8)
        bars10 = ax5.bar(x_pos + width/2, span_coverage, width, label='Span_11.2', color='#A23B72', alpha=0.8)
        ax5.set_xlabel('Network', fontweight='bold')
        ax5.set_ylabel('MDS Coverage (%)', fontweight='bold')
        ax5.set_title('5. MDS Coverage Ratio\n(Lower is Better)', fontweight='bold')
        ax5.set_xticks(x_pos)
        ax5.set_xticklabels(networks, rotation=15, ha='right')
        ax5.legend()
        ax5.grid(True, alpha=0.3, axis='y')
        # Add value labels
        for bars in [bars9, bars10]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax5.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # 6. Speed Comparison (Bottom Right)
        ax6 = axes[1, 2]
        seq_speed = [n/t if t > 0 else 0 for n, t in zip(num_nodes, seq_times)]
        span_speed = [n/t if t > 0 else 0 for n, t in zip(num_nodes, span_times)]
        bars11 = ax6.bar(x_pos - width/2, seq_speed, width, label='Seq_11.1', color='#2E86AB', alpha=0.8)
        bars12 = ax6.bar(x_pos + width/2, span_speed, width, label='Span_11.2', color='#A23B72', alpha=0.8)
        ax6.set_xlabel('Network', fontweight='bold')
        ax6.set_ylabel('Processing Speed (nodes/sec)', fontweight='bold')
        ax6.set_title('6. Processing Speed\n(Higher is Better)', fontweight='bold')
        ax6.set_xticks(x_pos)
        ax6.set_xticklabels(networks, rotation=15, ha='right')
        ax6.legend()
        ax6.grid(True, alpha=0.3, axis='y')
        # Add value labels
        for bars in [bars11, bars12]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax6.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        # Add mobility metrics if available (row 3)
        if has_mobility:
            # 7. Topology Stability (Topology Changes per Time Step)
            ax7 = axes[2, 0]
            bars13 = ax7.bar(x_pos, topology_stability, width=0.6, color='#F18F01', alpha=0.8, edgecolor='black', linewidth=1.5)
            ax7.set_xlabel('Network', fontweight='bold')
            ax7.set_ylabel('Connection Changes per Time Step', fontweight='bold')
            ax7.set_title('7. Topology Stability\n(Lower is More Stable)', fontweight='bold')
            ax7.set_xticks(x_pos)
            ax7.set_xticklabels(networks, rotation=15, ha='right')
            ax7.grid(True, alpha=0.3, axis='y')
            for bar in bars13:
                height = bar.get_height()
                if height > 0:
                    ax7.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            # 8. Average Edges
            ax8 = axes[2, 1]
            bars14 = ax8.bar(x_pos, avg_edges, width=0.6, color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1.5)
            ax8.set_xlabel('Network', fontweight='bold')
            ax8.set_ylabel('Average Number of Edges', fontweight='bold')
            ax8.set_title('8. Average Network Connectivity\n(Higher is More Connected)', fontweight='bold')
            ax8.set_xticks(x_pos)
            ax8.set_xticklabels(networks, rotation=15, ha='right')
            ax8.grid(True, alpha=0.3, axis='y')
            for bar in bars14:
                height = bar.get_height()
                if height > 0:
                    ax8.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            # 9. Average Degree
            ax9 = axes[2, 2]
            bars15 = ax9.bar(x_pos, avg_degree, width=0.6, color='#A23B72', alpha=0.8, edgecolor='black', linewidth=1.5)
            ax9.set_xlabel('Network', fontweight='bold')
            ax9.set_ylabel('Average Node Degree', fontweight='bold')
            ax9.set_title('9. Average Node Degree\n(Higher is More Connected)', fontweight='bold')
            ax9.set_xticks(x_pos)
            ax9.set_xticklabels(networks, rotation=15, ha='right')
            ax9.grid(True, alpha=0.3, axis='y')
            for bar in bars15:
                height = bar.get_height()
                if height > 0:
                    ax9.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        os.makedirs(RESULTS_DIR, exist_ok=True)
        filepath = os.path.join(RESULTS_DIR, 'comprehensive_results.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        logger.error(f"Error creating comprehensive results: {e}")
        import traceback
        logger.error(traceback.format_exc())


def plot_mobility_trace(trace_df, name: str, max_drones_to_plot: int = 20) -> None:
    """
    Mobilite izini 3D veya 2D projeksiyon olarak görselleştirir.
    
    Parameters
    ----------
    trace_df : pd.DataFrame
        Mobilite izi verisi (mobility.generate_gauss_markov_trace çıktısı)
    name : str
        Senaryo adı (dosya adlandırma için)
    max_drones_to_plot : int, optional
        Görselleştirilecek maksimum drone sayısı (performans için), varsayılan 20
    """
    try:
        import pandas as pd
        
        unique_drones = sorted(trace_df['node_id'].unique())
        n_drones = len(unique_drones)
        
        # Çok fazla drone varsa sadece bir kısmını göster
        if n_drones > max_drones_to_plot:
            drones_to_plot = unique_drones[::n_drones // max_drones_to_plot][:max_drones_to_plot]
        else:
            drones_to_plot = unique_drones
        
        # 2x2 subplot: 3D görünüm, XY projeksiyon, XZ projeksiyon, YZ projeksiyon
        fig = plt.figure(figsize=(16, 12))
        
        # 3D görünüm
        ax1 = fig.add_subplot(2, 2, 1, projection='3d')
        
        # Her drone için yol çiz
        colors = plt.cm.tab20(np.linspace(0, 1, len(drones_to_plot)))
        for idx, drone_id in enumerate(drones_to_plot):
            drone_data = trace_df[trace_df['node_id'] == drone_id].sort_values('time')
            ax1.plot(drone_data['x'], drone_data['y'], drone_data['z'], 
                    color=colors[idx], alpha=0.6, linewidth=1.5, label=f'Drone {drone_id}')
            # Başlangıç noktası
            ax1.scatter(drone_data.iloc[0]['x'], drone_data.iloc[0]['y'], 
                       drone_data.iloc[0]['z'], color=colors[idx], s=100, marker='o')
            # Bitiş noktası
            ax1.scatter(drone_data.iloc[-1]['x'], drone_data.iloc[-1]['y'], 
                       drone_data.iloc[-1]['z'], color=colors[idx], s=100, marker='s')
        
        ax1.set_xlabel('X (m)', fontweight='bold')
        ax1.set_ylabel('Y (m)', fontweight='bold')
        ax1.set_zlabel('Z (m)', fontweight='bold')
        ax1.set_title('3D Mobilite İzi', fontweight='bold', fontsize=12)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax1.set_xlim([0, 1000])
        ax1.set_ylim([0, 1000])
        ax1.set_zlim([0, 200])
        
        # XY projeksiyon (üstten görünüm)
        ax2 = fig.add_subplot(2, 2, 2)
        for idx, drone_id in enumerate(drones_to_plot):
            drone_data = trace_df[trace_df['node_id'] == drone_id].sort_values('time')
            ax2.plot(drone_data['x'], drone_data['y'], color=colors[idx], 
                    alpha=0.6, linewidth=1.5)
            ax2.scatter(drone_data.iloc[0]['x'], drone_data.iloc[0]['y'], 
                       color=colors[idx], s=50, marker='o', zorder=5)
            ax2.scatter(drone_data.iloc[-1]['x'], drone_data.iloc[-1]['y'], 
                       color=colors[idx], s=50, marker='s', zorder=5)
        ax2.set_xlabel('X (m)', fontweight='bold')
        ax2.set_ylabel('Y (m)', fontweight='bold')
        ax2.set_title('XY Projeksiyon (Üstten Görünüm)', fontweight='bold', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 1000])
        ax2.set_ylim([0, 1000])
        ax2.set_aspect('equal')
        
        # XZ projeksiyon (yan görünüm)
        ax3 = fig.add_subplot(2, 2, 3)
        for idx, drone_id in enumerate(drones_to_plot):
            drone_data = trace_df[trace_df['node_id'] == drone_id].sort_values('time')
            ax3.plot(drone_data['x'], drone_data['z'], color=colors[idx], 
                    alpha=0.6, linewidth=1.5)
            ax3.scatter(drone_data.iloc[0]['x'], drone_data.iloc[0]['z'], 
                       color=colors[idx], s=50, marker='o', zorder=5)
            ax3.scatter(drone_data.iloc[-1]['x'], drone_data.iloc[-1]['z'], 
                       color=colors[idx], s=50, marker='s', zorder=5)
        ax3.set_xlabel('X (m)', fontweight='bold')
        ax3.set_ylabel('Z (m)', fontweight='bold')
        ax3.set_title('XZ Projeksiyon (Yan Görünüm)', fontweight='bold', fontsize=12)
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim([0, 1000])
        ax3.set_ylim([0, 200])
        
        # YZ projeksiyon (diğer yan görünüm)
        ax4 = fig.add_subplot(2, 2, 4)
        for idx, drone_id in enumerate(drones_to_plot):
            drone_data = trace_df[trace_df['node_id'] == drone_id].sort_values('time')
            ax4.plot(drone_data['y'], drone_data['z'], color=colors[idx], 
                    alpha=0.6, linewidth=1.5)
            ax4.scatter(drone_data.iloc[0]['y'], drone_data.iloc[0]['z'], 
                       color=colors[idx], s=50, marker='o', zorder=5)
            ax4.scatter(drone_data.iloc[-1]['y'], drone_data.iloc[-1]['z'], 
                       color=colors[idx], s=50, marker='s', zorder=5)
        ax4.set_xlabel('Y (m)', fontweight='bold')
        ax4.set_ylabel('Z (m)', fontweight='bold')
        ax4.set_title('YZ Projeksiyon (Yan Görünüm)', fontweight='bold', fontsize=12)
        ax4.grid(True, alpha=0.3)
        ax4.set_xlim([0, 1000])
        ax4.set_ylim([0, 200])
        
        fig.suptitle(f'Mobilite İzi Görselleştirmesi: {name}', 
                    fontsize=14, fontweight='bold')
        
        os.makedirs(RESULTS_DIR, exist_ok=True)
        safe_name = name.replace(" ", "_")
        filepath = os.path.join(RESULTS_DIR, f"mobility_trace_{safe_name}.png")
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        logger.error(f"Error plotting mobility trace: {e}")
        import traceback
        logger.error(traceback.format_exc())


def plot_dynamic_topology_evolution(
    topologies: Dict[int, nx.Graph],
    name: str,
    snapshot_times: List[int] = None
) -> None:
    """
    Topoloji değişimini zaman içinde gösterir.
    
    Parameters
    ----------
    topologies : Dict[int, nx.Graph]
        Zaman adımı -> Graf mapping'i
    name : str
        Senaryo adı
    snapshot_times : List[int], optional
        Görselleştirilecek zaman anları, varsayılan [0, duration//2, duration-1]
    """
    try:
        if not topologies:
            logger.warning("Empty topologies dictionary, nothing to plot")
            return
        
        times = sorted(topologies.keys())
        duration = len(times)
        
        if snapshot_times is None:
            # Varsayılan: başlangıç, ortası, sonu
            snapshot_times = [times[0], times[duration // 2], times[-1]]
        else:
            # Sadece mevcut zamanları kullan
            snapshot_times = [t for t in snapshot_times if t in times]
        
        if not snapshot_times:
            snapshot_times = [times[0]]
        
        n_snapshots = len(snapshot_times)
        fig, axes = plt.subplots(1, n_snapshots, figsize=(6 * n_snapshots, 6))
        
        if n_snapshots == 1:
            axes = [axes]
        
        for idx, t in enumerate(snapshot_times):
            G = topologies[t]
            ax = axes[idx]
            
            # Pozisyon bilgisini al (3D'den 2D'ye dönüştür)
            pos = {}
            has_3d_pos = False
            for node_id in G.nodes():
                if 'pos' in G.nodes[node_id]:
                    node_pos = G.nodes[node_id]['pos']
                    # Eğer 3D pozisyon varsa (tuple/list uzunluğu 3), XY projeksiyonu kullan
                    if isinstance(node_pos, (tuple, list)) and len(node_pos) == 3:
                        pos[node_id] = (node_pos[0], node_pos[1])  # XY projeksiyonu (z eksenini kaldır)
                        has_3d_pos = True
                    elif isinstance(node_pos, (tuple, list)) and len(node_pos) == 2:
                        pos[node_id] = tuple(node_pos)
                    else:
                        pos[node_id] = node_pos
                else:
                    # Pozisyon yoksa spring layout kullan
                    pos = nx.spring_layout(G, seed=42)
                    break
            
            # Eğer hiç pozisyon yoksa spring layout kullan
            if not pos:
                pos = nx.spring_layout(G, seed=42)
            
            # Kenarları çiz
            nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3, width=1.0, 
                                  edge_color='gray')
            
            # Düğümleri çiz
            nx.draw_networkx_nodes(G, pos, ax=ax, node_size=100, 
                                 node_color='#2E86AB', alpha=0.8,
                                 edgecolors='black', linewidths=1.5)
            
            # Node ID'leri göster (küçük ağlar için)
            if len(G) <= 50:
                nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)
            
            ax.set_title(f'Topoloji (t={t}s)\n'
                        f'Nodes: {len(G)}, Edges: {G.number_of_edges()}, '
                        f'Avg Degree: {2*G.number_of_edges()/len(G) if len(G) > 0 else 0:.2f}',
                        fontweight='bold', fontsize=11)
            ax.axis('off')
            ax.set_aspect('equal')
        
        fig.suptitle(f'Dinamik Topoloji Evrimi: {name}', 
                    fontsize=14, fontweight='bold')
        
        os.makedirs(RESULTS_DIR, exist_ok=True)
        safe_name = name.replace(" ", "_")
        filepath = os.path.join(RESULTS_DIR, f"topology_evolution_{safe_name}.png")
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        logger.error(f"Error plotting topology evolution: {e}")
        import traceback
        logger.error(traceback.format_exc())


def plot_mobility_performance(results: List[Dict]) -> None:
    """
    Mobilite senaryoları için performans görselleştirmesi.
    Zaman içinde MDS boyutu değişimi ve topoloji metriklerini gösterir.
    
    Parameters
    ----------
    results : List[Dict]
        Sonuçlar listesi (mobilite metrikleri içermeli)
    """
    try:
        # Sadece mobilite senaryolarını filtrele
        mobility_results = [r for r in results if 'Mobile' in r.get('network', '')]
        
        if not mobility_results:
            logger.warning("No mobility scenarios found in results")
            return
        
        networks = [r['network'] for r in mobility_results]
        topology_stability = [r.get('topology_stability', 0.0) for r in mobility_results]
        avg_edges = [r.get('avg_edges', 0.0) for r in mobility_results]
        avg_degree = [r.get('avg_degree', 0.0) for r in mobility_results]
        seq_sizes = [r['seq_size'] for r in mobility_results]
        span_sizes = [r['span_size'] for r in mobility_results]
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12), constrained_layout=True)
        fig.suptitle('Mobilite Senaryoları Performans Analizi', 
                    fontsize=16, fontweight='bold')
        
        x_pos = np.arange(len(networks))
        width = 0.35
        
        # 1. MDS Size Comparison (Top Left)
        ax1 = axes[0, 0]
        bars1 = ax1.bar(x_pos - width/2, seq_sizes, width, label='Seq_11.1', color='#2E86AB', alpha=0.8)
        bars2 = ax1.bar(x_pos + width/2, span_sizes, width, label='Span_11.2', color='#A23B72', alpha=0.8)
        ax1.set_xlabel('Network', fontweight='bold')
        ax1.set_ylabel('MDS Size', fontweight='bold')
        ax1.set_title('1. MDS Boyutu Karşılaştırması\n(Dinamik Topoloji Ortalaması)', fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(networks, rotation=15, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        # 2. Topology Stability (Top Right)
        ax2 = axes[0, 1]
        bars3 = ax2.bar(x_pos, topology_stability, width=0.6, color='#F18F01', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax2.set_xlabel('Network', fontweight='bold')
        ax2.set_ylabel('Bağlantı Değişimi / Zaman Adımı', fontweight='bold')
        ax2.set_title('2. Topoloji Stabilitesi\n(Düşük = Daha Stabil)', fontweight='bold')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(networks, rotation=15, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')
        for bar in bars3:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 3. Average Edges (Bottom Left)
        ax3 = axes[1, 0]
        bars4 = ax3.bar(x_pos, avg_edges, width=0.6, color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax3.set_xlabel('Network', fontweight='bold')
        ax3.set_ylabel('Ortalama Kenar Sayısı', fontweight='bold')
        ax3.set_title('3. Ortalama Ağ Bağlantısı\n(Yüksek = Daha Bağlı)', fontweight='bold')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels(networks, rotation=15, ha='right')
        ax3.grid(True, alpha=0.3, axis='y')
        for bar in bars4:
            height = bar.get_height()
            if height > 0:
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # 4. Average Degree (Bottom Right)
        ax4 = axes[1, 1]
        bars5 = ax4.bar(x_pos, avg_degree, width=0.6, color='#A23B72', alpha=0.8, edgecolor='black', linewidth=1.5)
        ax4.set_xlabel('Network', fontweight='bold')
        ax4.set_ylabel('Ortalama Düğüm Derecesi', fontweight='bold')
        ax4.set_title('4. Ortalama Düğüm Derecesi\n(Yüksek = Daha Bağlı)', fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(networks, rotation=15, ha='right')
        ax4.grid(True, alpha=0.3, axis='y')
        for bar in bars5:
            height = bar.get_height()
            if height > 0:
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        os.makedirs(RESULTS_DIR, exist_ok=True)
        filepath = os.path.join(RESULTS_DIR, 'mobility_performance.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        logger.error(f"Error creating mobility performance plot: {e}")
        import traceback
        logger.error(traceback.format_exc())

