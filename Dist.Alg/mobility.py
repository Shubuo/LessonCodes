"""
Mobility Model Module for Drone Networks
Implements Gauss-Markov mobility model and dynamic topology generation
"""

import numpy as np
import pandas as pd
import networkx as nx
from scipy.spatial.distance import pdist, squareform
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# Simülasyon parametreleri
AREA_SIZE_X = 1000.0  # metre
AREA_SIZE_Y = 1000.0  # metre
AREA_SIZE_Z = 200.0   # metre
COMM_RANGE = 150.0    # metre (iletişim menzili)
MIN_SPEED = 10.0      # m/s
MAX_SPEED = 25.0      # m/s
ALPHA = 0.85          # Gauss-Markov alpha parametresi
DELTA_T = 1.0         # Zaman adımı (saniye)


def generate_gauss_markov_trace(
    n_drones: int,
    duration: int,
    alpha: float = ALPHA,
    area_size: Tuple[float, float, float] = (AREA_SIZE_X, AREA_SIZE_Y, AREA_SIZE_Z),
    speed_range: Tuple[float, float] = (MIN_SPEED, MAX_SPEED),
    seed: int = None
) -> pd.DataFrame:
    """
    Gauss-Markov hareket modeli ile mobilite izi üretir.
    
    Gauss-Markov modeli, gerçekçi drone hareketini simüle eder:
    - Önceki hızın bir kısmını korur (α * v_old)
    - Ortalama yöne doğru çeker ((1-α) * v_mean)
    - Rastgele gürültü ekler (sqrt(1-α²) * noise)
    
    Parameters
    ----------
    n_drones : int
        Drone sayısı
    duration : int
        Simülasyon süresi (saniye)
    alpha : float, optional
        Gauss-Markov alpha parametresi (0-1 arası, varsayılan 0.85)
    area_size : tuple, optional
        (x, y, z) alan boyutları (metre), varsayılan (1000, 1000, 200)
    speed_range : tuple, optional
        (min_speed, max_speed) hız aralığı (m/s), varsayılan (10, 25)
    seed : int, optional
        Rastgele sayı üreteci seed değeri
        
    Returns
    -------
    pd.DataFrame
        Mobilite izi verisi. Kolonlar: ['time', 'node_id', 'x', 'y', 'z', 'vx', 'vy', 'vz']
    """
    if seed is not None:
        np.random.seed(seed)
    
    area_x, area_y, area_z = area_size
    min_speed, max_speed = speed_range
    
    # Başlangıç pozisyonları (rastgele dağıtılmış)
    positions = np.random.rand(n_drones, 3) * np.array([area_x, area_y, area_z])
    
    # Başlangıç hız vektörleri (belirli bir yöne doğru + rastgele varyasyon)
    # Her drone için ortalama yön vektörü (normalize edilmiş)
    mean_directions = np.random.rand(n_drones, 3) - 0.5  # -0.5 ile 0.5 arası
    mean_directions = mean_directions / (np.linalg.norm(mean_directions, axis=1, keepdims=True) + 1e-10)
    
    # Başlangıç hızları (min-max arası)
    initial_speeds = np.random.uniform(min_speed, max_speed, n_drones)
    velocities = mean_directions * initial_speeds[:, np.newaxis]
    
    # Rastgele gürültü ekle
    velocities += np.random.normal(0, 1.0, (n_drones, 3))
    
    trace_data = []
    
    for t in range(duration):
        # Gauss-Markov güncellemesi
        # v_new = α * v_old + (1-α) * v_mean + sqrt(1-α²) * noise
        noise = np.random.normal(0, 2.0, (n_drones, 3))
        velocities = (
            alpha * velocities +
            (1 - alpha) * mean_directions * initial_speeds[:, np.newaxis] +
            np.sqrt(1 - alpha**2) * noise
        )
        
        # Hızı sınırla (min-max aralığında tut)
        speeds = np.linalg.norm(velocities, axis=1)
        speeds = np.clip(speeds, min_speed, max_speed)
        velocities = velocities / (np.linalg.norm(velocities, axis=1, keepdims=True) + 1e-10) * speeds[:, np.newaxis]
        
        # Pozisyon güncellemesi: P_yeni = P_eski + V * delta_t
        positions += velocities * DELTA_T
        
        # Sınır kontrolü (Bounce: sınırda yön değiştir)
        for i in range(n_drones):
            # X sınırı
            if positions[i, 0] < 0:
                positions[i, 0] = 0
                velocities[i, 0] = -velocities[i, 0] * 0.8  # Bounce with damping
            elif positions[i, 0] > area_x:
                positions[i, 0] = area_x
                velocities[i, 0] = -velocities[i, 0] * 0.8
            
            # Y sınırı
            if positions[i, 1] < 0:
                positions[i, 1] = 0
                velocities[i, 1] = -velocities[i, 1] * 0.8
            elif positions[i, 1] > area_y:
                positions[i, 1] = area_y
                velocities[i, 1] = -velocities[i, 1] * 0.8
            
            # Z sınırı (yükseklik)
            if positions[i, 2] < 0:
                positions[i, 2] = 0
                velocities[i, 2] = -velocities[i, 2] * 0.8
            elif positions[i, 2] > area_z:
                positions[i, 2] = area_z
                velocities[i, 2] = -velocities[i, 2] * 0.8
        
        # Veriyi kaydet
        for i in range(n_drones):
            trace_data.append({
                'time': t,
                'node_id': i,
                'x': positions[i, 0],
                'y': positions[i, 1],
                'z': positions[i, 2],
                'vx': velocities[i, 0],
                'vy': velocities[i, 1],
                'vz': velocities[i, 2]
            })
    
    return pd.DataFrame(trace_data)


def generate_dynamic_topology(
    trace_df: pd.DataFrame,
    comm_range: float = COMM_RANGE
) -> Dict[int, nx.Graph]:
    """
    Mobilite izinden dinamik topoloji oluşturur.
    
    Her zaman adımı için:
    1. Drone pozisyonlarını alır
    2. Öklid mesafelerini hesaplar
    3. İletişim menzili içindeki düğümleri bağlar
    4. NetworkX grafı oluşturur
    
    Parameters
    ----------
    trace_df : pd.DataFrame
        Mobilite izi verisi (generate_gauss_markov_trace çıktısı)
    comm_range : float, optional
        İletişim menzili (metre), varsayılan 150m
        
    Returns
    -------
    Dict[int, nx.Graph]
        Zaman adımı -> NetworkX grafı mapping'i
        {time: Graph}
    """
    topologies = {}
    
    unique_times = sorted(trace_df['time'].unique())
    
    for t in unique_times:
        df_t = trace_df[trace_df['time'] == t].copy()
        
        # Node ID'leri sıralı olmalı
        df_t = df_t.sort_values('node_id')
        
        # Pozisyonları al
        coords = df_t[['x', 'y', 'z']].values
        
        # Öklid mesafelerini hesapla
        if len(coords) > 1:
            dist_matrix = squareform(pdist(coords))
        else:
            # Tek düğüm varsa boş graf
            G = nx.Graph()
            if len(df_t) > 0:
                G.add_node(int(df_t.iloc[0]['node_id']))
            topologies[t] = G
            continue
        
        # Menzil içindeki düğümleri bağla
        adj_matrix = (dist_matrix <= comm_range).astype(int)
        np.fill_diagonal(adj_matrix, 0)  # Kendine döngü yok
        
        # NetworkX grafına dönüştür
        G = nx.from_numpy_array(adj_matrix)
        
        # Node ID'leri orijinal ID'lere eşle (eğer sıralı değilse)
        node_ids = df_t['node_id'].values.astype(int)
        if not np.array_equal(node_ids, np.arange(len(node_ids))):
            # Node ID'leri yeniden etiketle
            mapping = {i: node_ids[i] for i in range(len(node_ids))}
            G = nx.relabel_nodes(G, mapping)
        
        # Pozisyon bilgisini node attribute olarak ekle
        for idx, row in df_t.iterrows():
            node_id = int(row['node_id'])
            if node_id in G.nodes():
                G.nodes[node_id]['pos'] = (row['x'], row['y'], row['z'])
        
        topologies[t] = G
    
    return topologies


def calculate_topology_metrics(topologies: Dict[int, nx.Graph]) -> Dict[str, list]:
    """
    Dinamik topolojiler için metrikler hesaplar.
    
    Parameters
    ----------
    topologies : Dict[int, nx.Graph]
        Zaman adımı -> Graf mapping'i
        
    Returns
    -------
    Dict[str, list]
        Metrikler: {
            'time': zaman adımları,
            'num_edges': kenar sayıları,
            'avg_degree': ortalama dereceler,
            'num_components': bağlı bileşen sayıları
        }
    """
    times = sorted(topologies.keys())
    num_edges = []
    avg_degrees = []
    num_components = []
    
    for t in times:
        G = topologies[t]
        num_edges.append(G.number_of_edges())
        
        if len(G) > 0:
            degrees = [d for n, d in G.degree()]
            avg_degrees.append(np.mean(degrees) if degrees else 0.0)
        else:
            avg_degrees.append(0.0)
        
        num_components.append(nx.number_connected_components(G))
    
    return {
        'time': times,
        'num_edges': num_edges,
        'avg_degree': avg_degrees,
        'num_components': num_components
    }


def calculate_connection_changes(
    topologies: Dict[int, nx.Graph]
) -> Dict[str, list]:
    """
    Zaman içinde bağlantı değişimlerini hesaplar.
    
    Parameters
    ----------
    topologies : Dict[int, nx.Graph]
        Zaman adımı -> Graf mapping'i
        
    Returns
    -------
    Dict[str, list]
        {
            'time': zaman adımları (t-1'den t'ye geçişler),
            'edges_added': eklenen kenar sayıları,
            'edges_removed': kaldırılan kenar sayıları,
            'total_changes': toplam değişim sayısı
        }
    """
    times = sorted(topologies.keys())
    edges_added = []
    edges_removed = []
    total_changes = []
    
    prev_edges = set()
    
    for t in times:
        G = topologies[t]
        current_edges = set(G.edges())
        
        if t == times[0]:
            # İlk zaman adımı için değişim yok
            edges_added.append(0)
            edges_removed.append(0)
            total_changes.append(0)
        else:
            # Önceki zaman adımından farkları hesapla
            added = len(current_edges - prev_edges)
            removed = len(prev_edges - current_edges)
            total = added + removed
            
            edges_added.append(added)
            edges_removed.append(removed)
            total_changes.append(total)
        
        prev_edges = current_edges
    
    return {
        'time': times,
        'edges_added': edges_added,
        'edges_removed': edges_removed,
        'total_changes': total_changes
    }

