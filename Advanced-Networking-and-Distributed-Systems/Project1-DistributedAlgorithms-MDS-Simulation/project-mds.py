"""
Distributed Algorithm Design and Analysis Course Project
Topic: Performance Evaluation of Dominating Set Algorithms (Seq_MDS vs Span_MDS)
Scenario: Drone Ad-Hoc Networks (FANET) & Real-World Datasets

================================================================================
PROJE AÇIKLAMASI:
================================================================================
Bu proje, Minimum Dominating Set (MDS) problemi için iki farkli algoritmanin
performansini karşilaştirmaktadir:

1. Seq_MDS (Algorithm 11.1): Merkezi (Centralized) Greedy Algoritma
   - Tüm graf bilgisine sahip merkezi bir node tarafindan çaliştirilir
   - Her iterasyonda en yüksek "span" değerine sahip node'u seçer
   - Mesaj göndermez (merkezi olduğu için)
   - Hizli ama ölçeklenebilir değil

2. Span_MDS (Algorithm 11.2): Dağitik (Distributed) Algoritma
   - Her node kendi kararlarini verir, komşulariyla mesajlaşir
   - Local maxima hesaplamasi yapar (span değerine göre)
   - Mesaj gönderir (dağitik olduğu için)
   - Yavaş ama ölçeklenebilir ve fault-tolerant

TEST SENARYOLARI:
- Dynamic Mobility Scenarios: Gauss-Markov mobilite modeli ile dinamik drone hareketi

ÇIKTILAR:
- Performans grafikleri (PNG formatinda)
- Detayli analiz raporu (TXT formatinda)
- Terminal çiktilari

Author: Burak YORUK
Date: Dec 2025
"""

import random
import logging
import sys
import warnings
from typing import List, Dict
import numpy as np
from tqdm import tqdm

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
# Bu bölümde simülasyon ve algoritma parametreleri tanimlanmiştir.

RANDOM_SEED = 80
# Rastgele sayi üreteci için seed değeri
# Ayni seed ile çaliştirildiğinda ayni sonuçlari üretir (reproducibility)

MAX_SIMULATION_ROUNDS = 50
# Dağitik algoritma için maksimum round sayisi
# Algoritma bu kadar round içinde sonlanmazsa durdurulur (safety limit)

SIMULATION_TIME_CHUNK = 1.0
# Simülasyon zaman dilimi (saniye)
# Her round arasindaki zaman araliği

MIN_NETWORK_DELAY = 0.01
# Minimum ağ gecikmesi (saniye)
# Mesajlarin iletilmesi için minimum süre

MAX_NETWORK_DELAY = 0.05
# Maksimum ağ gecikmesi (saniye)
# Mesajlarin iletilmesi için maksimum süre
# Gerçekçi bir simülasyon için rastgele gecikme kullanilir

ROUND_BUFFER_TIME = 0.1
# Round'lar arasi bekleme süresi (saniye)
# Her round sonrasi ek bekleme süresi

MAX_GRAPH_SIZE_FOR_SIMULATION = 2000
# Simülasyon için maksimum graf boyutu (node sayisi)
# Büyük graflar için alt graf alinir (performans için)


# Configure logging - only show errors (suppress warnings)
logging.basicConfig(
    level=logging.ERROR,  # Only errors
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Import modules
# Algoritma implementasyonlari
from algorithms import run_seq_mds, run_span_mds_simulation
# Graf olusturma ve gorsellestirme fonksiyonlari
from visualization import (
    generate_drone_network,
    plot_comprehensive_results,
    plot_network_layout,  # topoloji gorseli icin
    plot_mobility_trace,
    plot_dynamic_topology_evolution,
    plot_mobility_performance,
)
# Mobilite modeli
from mobility import (
    generate_gauss_markov_trace,
    generate_dynamic_topology,
    calculate_topology_metrics,
    calculate_connection_changes,
)
# Analiz ve raporlama fonksiyonlari
from analysis import save_findings_to_file, print_findings_summary, generate_detailed_analysis


def run_experiments() -> None:
    """
    Ana deney fonksiyonu: Her iki algoritmayi dinamik mobilite senaryolarında test eder.
    
    Bu fonksiyon şu adimlari takip eder:
    1. Her mobilite senaryosu için Gauss-Markov mobilite izi üretir
    2. Dinamik topolojiler oluşturur (her zaman adımı için)
    3. Her zaman adımında algoritmaları çalıştırır ve sonuçları toplar
    4. Ortalama sonuçlari görselleştirir (grafikler) ve analiz eder (raporlar)
    
    Test Senaryolari:
    - Mobile_Small_Swarm: 20 drone, 600 saniye, mobilite
    - Mobile_Medium_Swarm: 35 drone, 600 saniye, mobilite
    - Mobile_Large_Swarm: 50 drone, 600 saniye, mobilite
    
    Ölçülen Metrikler:
    - MDS Size: Dominating set'in boyutu (küçük = daha iyi)
    - Execution Time: Çalişma süresi (hizli = daha iyi)
    - Message Count: Gönderilen mesaj sayisi (az = daha iyi, sadece Span için)
    - Topology Stability: Topoloji değişim oranı
    - Connection Changes: Zaman adımı başına bağlantı değişim sayısı
    
    Returns:
        None (sonuçlar dosyalara ve terminale yazdirilir)
    """
    # ========================================================================
    # STEP 1: HEADER AND SETTINGS
    # ========================================================================
    print("=" * 75)
    print(" DISTRIBUTED ALGORITHM PROJECT: MDS PERFORMANCE EVALUATION")
    print(" Dynamic Mobility Scenarios with Gauss-Markov Model")
    print("=" * 75)
    
    # Test parameters
    NUM_SEEDS = 5  # Her senaryo için seed sayısı (performans için azaltıldı)
    SEED_START = 1
    SEED_END = NUM_SEEDS
    SIMULATION_DURATION = 600  # saniye
    
    # Sonuçlari saklamak için liste (grafik ve analiz için)
    results: List[Dict] = []

    # ========================================================================
    # STEP 2: MOBILITY SCENARIOS (DYNAMIC DRONE SWARM SIMULATION)
    # ========================================================================
    # Using Gauss-Markov mobility model to simulate realistic drone movement
    
    mobility_scenarios = [
        ("Mobile_Small_Swarm", 20, SIMULATION_DURATION),   # Small: 20 drones, 600s
        ("Mobile_Medium_Swarm", 35, SIMULATION_DURATION),  # Medium: 35 drones, 600s
        ("Mobile_Large_Swarm", 50, SIMULATION_DURATION),   # Large: 50 drones, 600s
    ]
    # Each scenario: (name, n_drones, duration)

    for scenario_idx, (name, n_drones, duration) in enumerate(mobility_scenarios):
        print(f"\n{'='*75}")
        print(f" Processing {name}: {n_drones} drones, {duration}s simulation")
        print(f"{'='*75}")
        
        # Lists to collect results across all seeds and time steps
        all_seq_sizes = []
        all_span_sizes = []
        all_seq_times = []
        all_span_times = []
        all_seq_msgs = []
        all_span_msgs = []
        all_num_nodes = []
        
        # Topology metrics
        all_topology_metrics = []
        all_connection_changes = []
        
        # Store first seed's data for visualization
        first_trace_df = None
        first_topologies = None
        
        # Run tests for each seed
        successful_runs = 0
        
        seed_pbar = tqdm(
            total=SEED_END - SEED_START + 1,
            desc=f"{name:25s}",
            leave=False,
            ncols=120,
            position=0,
            ascii=True,
            file=sys.stdout
        )
        
        try:
            for seed in range(SEED_START, SEED_END + 1):
                seed_pbar.update(1)
                try:
                    # Set seed
                    random.seed(seed)
                    np.random.seed(seed)
                    
                    # Generate mobility trace using Gauss-Markov model
                    trace_df = generate_gauss_markov_trace(
                        n_drones=n_drones,
                        duration=duration,
                        seed=seed
                    )
                    
                    if trace_df.empty:
                        continue
                    
                    # Store first seed's trace for visualization
                    if first_trace_df is None:
                        first_trace_df = trace_df.copy()
                    
                    # Generate dynamic topologies
                    topologies = generate_dynamic_topology(trace_df)
                    
                    if not topologies:
                        continue
                    
                    # Store first seed's topologies for visualization
                    if first_topologies is None:
                        first_topologies = topologies.copy()
                    
                    # Calculate topology metrics
                    topology_metrics = calculate_topology_metrics(topologies)
                    connection_changes = calculate_connection_changes(topologies)
                    
                    all_topology_metrics.append(topology_metrics)
                    all_connection_changes.append(connection_changes)
                    
                    # Run algorithms on each time step
                    time_step_results = {
                        'seq_sizes': [],
                        'span_sizes': [],
                        'seq_times': [],
                        'span_times': [],
                        'seq_msgs': [],
                        'span_msgs': [],
                        'num_nodes': []
                    }
                    
                    # Sample time steps to reduce computation (her 10. zaman adımında)
                    time_steps = sorted(topologies.keys())
                    sampled_times = time_steps[::10]  # Her 10 saniyede bir
                    if not sampled_times:
                        sampled_times = time_steps[:10]  # En az 10 örnek
                    
                    time_pbar = tqdm(
                        total=len(sampled_times),
                        desc=f"  Seed {seed}",
                        leave=False,
                        ncols=100,
                        position=1,
                        ascii=True,
                        file=sys.stdout
                    )
                    
                    for t in sampled_times:
                        time_pbar.update(1)
                        G = topologies[t]
                        
                        if len(G) == 0:
                            continue
                        
                        # Run Seq_11.1 Algorithm (Centralized)
                        try:
                            ds_seq, time_seq, msgs_seq = run_seq_mds(G)
                            time_step_results['seq_sizes'].append(len(ds_seq))
                            time_step_results['seq_times'].append(time_seq)
                            time_step_results['seq_msgs'].append(msgs_seq)
                        except Exception as e:
                            logger.error(f"Error in seq_mds at t={t}: {e}")
                            continue
                        
                        # Run Span_11.2 Algorithm (Distributed)
                        try:
                            ds_span, time_span, msgs, rounds = run_span_mds_simulation(G)
                            time_step_results['span_sizes'].append(len(ds_span))
                            time_step_results['span_times'].append(time_span)
                            time_step_results['span_msgs'].append(msgs)
                        except Exception as e:
                            logger.error(f"Error in span_mds at t={t}: {e}")
                            continue
                        
                        time_step_results['num_nodes'].append(len(G))
                    
                    time_pbar.close()
                    
                    # Collect results (average over time steps for this seed)
                    if time_step_results['seq_sizes']:
                        all_seq_sizes.extend(time_step_results['seq_sizes'])
                        all_span_sizes.extend(time_step_results['span_sizes'])
                        all_seq_times.extend(time_step_results['seq_times'])
                        all_span_times.extend(time_step_results['span_times'])
                        all_seq_msgs.extend(time_step_results['seq_msgs'])
                        all_span_msgs.extend(time_step_results['span_msgs'])
                        all_num_nodes.extend(time_step_results['num_nodes'])
                        successful_runs += 1
                        
                except Exception as e:
                    logger.error(f"Error processing seed {seed} for {name}: {e}")
                    continue
        finally:
            seed_pbar.close()
        
        # Calculate averages
        if successful_runs > 0 and len(all_seq_sizes) > 0:
            avg_seq_size = np.mean(all_seq_sizes)
            avg_span_size = np.mean(all_span_sizes)
            avg_seq_time = np.mean(all_seq_times)
            avg_span_time = np.mean(all_span_times)
            avg_seq_msgs = np.mean(all_seq_msgs)
            avg_span_msgs = np.mean(all_span_msgs)
            avg_num_nodes = np.mean(all_num_nodes)
            
            # Calculate topology stability (average connection changes per time step)
            avg_connection_changes = 0.0
            if all_connection_changes:
                total_changes = sum([sum(cc['total_changes']) for cc in all_connection_changes])
                total_time_steps = sum([len(cc['time']) for cc in all_connection_changes])
                if total_time_steps > 0:
                    avg_connection_changes = total_changes / total_time_steps
                else:
                    avg_connection_changes = 0.0
            
            # Calculate average topology metrics
            avg_edges = 0.0
            avg_degree = 0.0
            if all_topology_metrics:
                total_edges = sum([sum(tm['num_edges']) for tm in all_topology_metrics])
                total_degrees = sum([sum(tm['avg_degree']) for tm in all_topology_metrics])
                total_steps = sum([len(tm['time']) for tm in all_topology_metrics])
                if total_steps > 0:
                    avg_edges = total_edges / total_steps
                    avg_degree = total_degrees / total_steps
            
            print(
                f"{name:25s} - Completed: {successful_runs} seeds | "
                f"Seq: MDS={avg_seq_size:.2f}, Time={avg_seq_time:.6f}s | "
                f"Span: MDS={avg_span_size:.2f}, Time={avg_span_time:.6f}s | "
                f"Topology: {avg_edges:.1f} edges, {avg_degree:.2f} avg degree"
            )

            # Save results
            results.append({
                'network': name,
                'num_nodes': int(avg_num_nodes),
                'seq_size': avg_seq_size,
                'span_size': avg_span_size,
                'seq_time': avg_seq_time,
                'span_time': avg_span_time,
                'seq_msgs': avg_seq_msgs,
                'span_msgs': avg_span_msgs,
                'topology_stability': avg_connection_changes,
                'avg_edges': avg_edges,
                'avg_degree': avg_degree
            })
            
            # Create visualizations for first seed
            if first_trace_df is not None and first_topologies is not None:
                try:
                    plot_mobility_trace(first_trace_df, name)
                    plot_dynamic_topology_evolution(first_topologies, name)
                except Exception as e:
                    logger.error(f"Error creating visualizations for {name}: {e}")
        else:
            print(f"  WARNING: No successful runs for {name}, skipping...")

    # ========================================================================
    # STEP 3: PRINT AVERAGE RESULTS
    # ========================================================================
    # Show average results in table format after all tests complete
    
    if results:
        print("\n" + "=" * 75)
        print(" AVERAGE RESULTS (from 100 seed tests)")
        print("=" * 75)
        print(f"{'Network':<20} | {'Alg':<10} | {'MDS Size':<10} | {'Time(s)':<10} | {'Msgs':<10}")
        print("-" * 75)
        
        for r in results:
            print(f"{r['network']:<20} | {'Seq_11.1':<10} | {r['seq_size']:<10.2f} | {r['seq_time']:<10.6f} | {r['seq_msgs']:<10.0f}")
            print(f"{r['network']:<20} | {'Span_11.2':<10} | {r['span_size']:<10.2f} | {r['span_time']:<10.6f} | {r['span_msgs']:<10.0f}")
            print("-" * 75)
    
    # ========================================================================
    # STEP 4: VISUALIZATION AND ANALYSIS
    # ========================================================================
    # Visualize and analyze results after all tests complete
    
    if results:
        print("\nGenerating visualizations and reports...")
        # 1. Comprehensive single visualization (all metrics in one figure)
        plot_comprehensive_results(results)
        
        # 2. Mobility-specific performance visualization
        plot_mobility_performance(results)
        
        # 3. Save findings to file (results/bulgular_raporu.txt)
        # Detailed analysis, scenario-based findings and algorithm selection guide
        save_findings_to_file(results)
        
        # 4. Print findings to terminal
        # Short summary and main findings
        print_findings_summary(results)
        
        print("\nAll results saved to 'results' directory.")
    else:
        # Warn if no results
        logger.warning("No results to plot or save")


if __name__ == "__main__":
    """
    Programin giriş noktasi.
    
    Bu dosya doğrudan çaliştirildiğinda (python project-mds.py),
    run_experiments() fonksiyonu çağrilir ve tüm deneyler başlatilir.
    
    Modül olarak import edildiğinde bu kod çalişmaz.
    """
    run_experiments()
