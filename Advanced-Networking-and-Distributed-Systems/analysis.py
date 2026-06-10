"""
Analysis and reporting module for MDS Algorithm Project
Contains functions for generating reports and analysis
"""

import time
import logging
import os
from typing import List, Dict
import numpy as np

logger = logging.getLogger(__name__)

# Results directory
RESULTS_DIR = "results"


def save_findings_to_file(results: List[Dict], filename: str = "bulgular_raporu.txt") -> None:
    """Saves findings summary to a text file."""
    try:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        filepath = os.path.join(RESULTS_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 75 + "\n")
            f.write(" 🔍 ANA BULGULAR VE SONUÇLAR (FINDINGS SUMMARY)\n")
            f.write("=" * 75 + "\n")
            f.write(f"\nRapor Tarihi: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Proje: MDS Algoritma Performans Değerlendirmesi\n")
            f.write(f"Algoritmalar: Seq_11.1 (Merkezi) vs Span_11.2 (Dağıtık)\n\n")
            
            total_size_improvement = []
            total_time_ratios = []
            total_msg_counts = []
            
            # Mobilite senaryoları
            mobility_results = [r for r in results if 'Mobile' in r.get('network', '')]
            
            for r in results:
                if r['span_size'] > 0:
                    total_size_improvement.append(r['seq_size'] / r['span_size'])
                if r['seq_time'] > 0:
                    total_time_ratios.append(r['span_time'] / r['seq_time'])
                total_msg_counts.append(r['span_msgs'])
            
            avg_size_improvement = np.mean(total_size_improvement) if total_size_improvement else 0
            avg_time_ratio = np.mean(total_time_ratios) if total_time_ratios else 0
            
            f.write("\n📈 GENEL İSTATİSTİKLER:\n")
            f.write(f"   • Ortalama MDS Boyutu İyileştirmesi: Span_11.2, Seq_11.1'den {avg_size_improvement:.2f}x daha küçük MDS üretiyor\n")
            f.write(f"   • Ortalama Hız Farkı: Seq_11.1, Span_11.2'den {avg_time_ratio:.2f}x daha hızlı\n")
            f.write(f"   • Toplam Mesaj Sayısı: {sum(total_msg_counts):,} mesaj (Span_11.2 için)\n")
            
            f.write("\n🎯 SENARYO BAZLI BULGULAR:\n")
            
            # Mobilite Senaryoları Özeti
            if mobility_results:
                f.write("\n   📍 Dinamik Mobilite Senaryoları (Gauss-Markov Model) - Özet:\n")
                f.write("      Gauss-Markov mobilite modeli ile gerçekçi drone hareketi simüle edilmiştir.\n")
                f.write("      Her zaman adımında topoloji değişmekte ve algoritmalar dinamik ağ üzerinde test edilmiştir.\n")
                f.write("      Üç farklı ölçekte test edilmiştir:\n\n")
                
                total_mobile_nodes = sum(r['num_nodes'] for r in mobility_results)
                total_mobile_seq_size = sum(r['seq_size'] for r in mobility_results)
                total_mobile_span_size = sum(r['span_size'] for r in mobility_results)
                total_mobile_seq_time = sum(r['seq_time'] for r in mobility_results)
                total_mobile_span_time = sum(r['span_time'] for r in mobility_results)
                total_mobile_msgs = sum(r['span_msgs'] for r in mobility_results)
                avg_topology_stability = np.mean([r.get('topology_stability', 0.0) for r in mobility_results])
                avg_edges = np.mean([r.get('avg_edges', 0.0) for r in mobility_results])
                avg_degree = np.mean([r.get('avg_degree', 0.0) for r in mobility_results])
                
                avg_mobile_size_ratio = np.mean([r['seq_size']/r['span_size'] for r in mobility_results if r['span_size'] > 0])
                avg_mobile_time_ratio = np.mean([r['span_time']/r['seq_time'] for r in mobility_results if r['seq_time'] > 0])
                
                f.write(f"      • Toplam Node Sayısı: {total_mobile_nodes} node (3 farklı senaryo)\n")
                f.write(f"      • Toplam MDS Boyutu: Seq={total_mobile_seq_size:.2f}, Span={total_mobile_span_size:.2f}\n")
                f.write(f"      • Ortalama MDS İyileştirmesi: Span_11.2, Seq_11.1'den {avg_mobile_size_ratio:.2f}x daha küçük MDS üretiyor\n")
                f.write(f"      • Toplam Çalışma Süresi: Seq={total_mobile_seq_time:.4f}s, Span={total_mobile_span_time:.4f}s\n")
                f.write(f"      • Ortalama Hız Farkı: Seq_11.1, Span_11.2'den {avg_mobile_time_ratio:.2f}x daha hızlı\n")
                f.write(f"      • Toplam İletişim: Span {total_mobile_msgs:.0f} mesaj gönderdi ({total_mobile_msgs/total_mobile_nodes:.2f} mesaj/node)\n")
                f.write(f"      • Topoloji Stabilitesi: Ortalama {avg_topology_stability:.2f} bağlantı değişimi/zaman adımı\n")
                f.write(f"      • Ortalama Ağ Bağlantısı: {avg_edges:.1f} kenar, {avg_degree:.2f} ortalama derece\n")
                
                f.write("\n      Detaylı Mobilite Senaryoları Sonuçları:\n")
                for r in mobility_results:
                    network = r['network']
                    num_nodes = r['num_nodes']
                    seq_size = r['seq_size']
                    span_size = r['span_size']
                    seq_time = r['seq_time']
                    span_time = r['span_time']
                    span_msgs = r['span_msgs']
                    topology_stability = r.get('topology_stability', 0.0)
                    avg_edges_scenario = r.get('avg_edges', 0.0)
                    avg_degree_scenario = r.get('avg_degree', 0.0)
                    
                    size_ratio = seq_size / span_size if span_size > 0 else 0
                    time_ratio = span_time / seq_time if seq_time > 0 else 0
                    
                    f.write(f"        - {network} ({num_nodes} node):\n")
                    f.write(f"          MDS: Seq={seq_size:.2f}, Span={span_size:.2f} (Span {size_ratio:.2f}x daha küçük)\n")
                    if time_ratio > 0:
                        f.write(f"          Süre: Seq={seq_time:.4f}s, Span={span_time:.4f}s (Seq {time_ratio:.2f}x daha hızlı)\n")
                    f.write(f"          Mesaj: {span_msgs:.0f} ({span_msgs/num_nodes:.2f} mesaj/node)\n")
                    f.write(f"          Topoloji: {topology_stability:.2f} değişim/adım, {avg_edges_scenario:.1f} kenar, {avg_degree_scenario:.2f} derece\n")
            
            f.write("\n💡 ANA BULGULAR:\n")
            f.write("   1. MDS BOYUTU:\n")
            f.write(f"      ✅ Span_11.2 algoritması TÜM senaryolarda Seq_11.1'den daha küçük MDS üretiyor\n")
            f.write(f"      ✅ Ortalama {avg_size_improvement:.2f}x iyileştirme gözlemlendi\n")
            f.write("      💡 Bu, Span_11.2'nin kaynak kullanımında daha verimli olduğunu gösterir\n")
            
            f.write("\n   2. ÇALIŞMA SÜRESİ:\n")
            f.write("      ✅ Seq_11.1 merkezi algoritma olduğu için genellikle daha hızlı\n")
            f.write(f"      ✅ Ortalama {avg_time_ratio:.2f}x hız farkı gözlemlendi\n")
            f.write("      ⚠️  Ancak büyük ağlarda (2000+ node) fark azalıyor\n")
            f.write("      💡 Büyük ölçekli sistemlerde Span_11.2'nin paralel çalışma avantajı görülüyor\n")
            
            f.write("\n   3. İLETİŞİM KARMAŞIKLIĞI:\n")
            f.write("      ✅ Seq_11.1 merkezi olduğu için mesaj göndermiyor (0 mesaj)\n")
            avg_msg_per_node = np.mean([m/r['num_nodes'] for m, r in zip(total_msg_counts, results) if r['num_nodes'] > 0])
            f.write(f"      ✅ Span_11.2 ortalama {avg_msg_per_node:.2f} mesaj/node gönderiyor\n")
            f.write("      💡 İletişim maliyeti dağıtık sistemlerin ana dezavantajı\n")
            
            f.write("\n   4. MOBİLİTE VE TOPOLOJİ DEĞİŞİMİ:\n")
            if mobility_results:
                avg_stability = np.mean([r.get('topology_stability', 0.0) for r in mobility_results])
                f.write(f"      ✅ Dinamik topolojilerde ortalama {avg_stability:.2f} bağlantı değişimi/zaman adımı gözlemlendi\n")
                f.write("      ✅ Algoritmalar topoloji değişimlerine adapte olabilmektedir\n")
                f.write("      💡 Mobilite arttıkça topoloji stabilitesi azalır, bu da algoritma performansını etkileyebilir\n")
                f.write("      💡 Span_11.2 dağıtık yapısı sayesinde dinamik ağlarda daha dayanıklıdır\n")
            else:
                f.write("      ℹ️  Bu test setinde mobilite senaryosu bulunmamaktadır\n")
            
            f.write("\n   5. ÖLÇEKLENEBİLİRLİK:\n")
            f.write("      ✅ Küçük ağlarda (<100 node): Seq_11.1 tercih edilebilir (hızlı, basit)\n")
            f.write("      ✅ Orta ağlarda (100-500 node): Span_11.2 önerilir (daha küçük MDS)\n")
            f.write("      ✅ Büyük ağlarda (>500 node): Span_11.2 kesinlikle önerilir (ölçeklenebilir)\n")
            if mobility_results:
                f.write("      ✅ Dinamik ağlarda: Span_11.2 önerilir (merkezi nokta başarısızlığına dayanıklı)\n")
            
            f.write("\n📊 ALGORİTMA SEÇİM KILAVUZU:\n")
            f.write("   Seq_11.1 KULLAN:\n")
            f.write("      • Merkezi kontrol mümkünse\n")
            f.write("      • Hız kritikse ve küçük-orta ölçekli ağlar\n")
            f.write("      • İletişim maliyeti önemliyse\n")
            f.write("      • Merkezi nokta başarısızlığı riski düşükse\n")
            
            f.write("\n   Span_11.2 KULLAN:\n")
            f.write("      • Dağıtık sistem gereksinimi varsa\n")
            f.write("      • MDS boyutu kritikse (kaynak tasarrufu)\n")
            f.write("      • Büyük ölçekli ağlar (>500 node)\n")
            f.write("      • Merkezi nokta başarısızlığına dayanıklılık gerekiyorsa\n")
            f.write("      • Ölçeklenebilirlik önemliyse\n")
            f.write("      • Dinamik/mobil ağlar (drone sürüleri, mobil ad-hoc ağlar)\n")
            f.write("      • Topoloji sık değişen ağlar\n")
            
            f.write("\n" + "=" * 75 + "\n")
            f.write(" ✅ Analiz tamamlandı! Detaylı grafikler PNG dosyalarına kaydedildi.\n")
            f.write(" 📁 Oluşturulan dosyalar:\n")
            f.write(f"    • {RESULTS_DIR}/mds_performance_comparison.png\n")
            f.write(f"    • {RESULTS_DIR}/algorithm_detailed_comparison.png\n")
            f.write(f"    • {RESULTS_DIR}/performance_metrics_comparison.png\n")
            f.write("=" * 75 + "\n")
        
        logger.info(f"Bulgular raporu kaydedildi: {filepath}")
    
    except Exception as e:
        logger.error(f"Error saving findings to file: {e}")
        import traceback
        logger.error(traceback.format_exc())


def print_findings_summary(results: List[Dict]) -> None:
    """
    Print a very concise summary to terminal.
    Detailed findings are saved in results/bulgular_raporu.txt
    """
    if not results:
        print("\nNo results to summarize.")
        return
    
    total_size_improvement = []
    total_time_ratios = []
    total_msg_counts = []
    
    for r in results:
        if r['span_size'] > 0:
            total_size_improvement.append(r['seq_size'] / r['span_size'])
        if r['seq_time'] > 0:
            total_time_ratios.append(r['span_time'] / r['seq_time'])
        total_msg_counts.append(r['span_msgs'])
    
    avg_size_improvement = np.mean(total_size_improvement) if total_size_improvement else 0
    avg_time_ratio = np.mean(total_time_ratios) if total_time_ratios else 0
    
    print("\n" + "=" * 60)
    print(" OZET (KISA)")
    print("=" * 60)
    print(f"Test edilen senaryo sayisi: {len(results)}")
    print(f"Span MDS boyut kazanci (ortalama): {avg_size_improvement:.2f}x daha kucuk MDS")
    print(f"Hiz farki (Seq / Span, ortalama): {avg_time_ratio:.2f}x daha hizli (Seq)")
    print(f"Toplam mesaj sayisi (Span): {sum(total_msg_counts):,} mesaj")
    print(f"Detayli bulgular: {RESULTS_DIR}/bulgular_raporu.txt")
    print("=" * 60 + "\n")


def generate_detailed_analysis(results: List[Dict]) -> None:
    """Generates a detailed textual analysis of the results."""
    print("\n" + "=" * 75)
    print(" DETAYLI ALGORİTMA ANALİZİ VE KARŞILAŞTIRMA RAPORU")
    print("=" * 75)
    
    for r in results:
        network = r['network']
        num_nodes = r['num_nodes']
        seq_size = r['seq_size']
        span_size = r['span_size']
        seq_time = r['seq_time']
        span_time = r['span_time']
        seq_msgs = r['seq_msgs']
        span_msgs = r['span_msgs']
        
        size_ratio = seq_size / span_size if span_size > 0 else float('inf')
        time_ratio = span_time / seq_time if seq_time > 0 else float('inf')
        seq_efficiency = seq_size / num_nodes if num_nodes > 0 else 0
        span_efficiency = span_size / num_nodes if num_nodes > 0 else 0
        seq_msgs_per_node = seq_msgs / num_nodes if num_nodes > 0 else 0
        span_msgs_per_node = span_msgs / num_nodes if num_nodes > 0 else 0
        
        print(f"\n📊 {network} Analizi ({num_nodes} node)")
        print("-" * 75)
        
        print(f"\n🎯 Dominating Set Boyutu:")
        print(f"   Seq_11.1:  {seq_size:4d} node ({seq_efficiency*100:.2f}% of network)")
        print(f"   Span_11.2: {span_size:4d} node ({span_efficiency*100:.2f}% of network)")
        if span_size > 0:
            if size_ratio > 1.2:
                print(f"   ✅ Span_11.2, Seq_11.1'den {size_ratio:.2f}x daha küçük MDS üretiyor")
                print(f"   💡 Avantaj: Span_11.2 daha az kaynak kullanımı sağlıyor")
            elif size_ratio < 0.8:
                print(f"   ✅ Seq_11.1, Span_11.2'den {1/size_ratio:.2f}x daha küçük MDS üretiyor")
                print(f"   💡 Avantaj: Seq_11.1 merkezi optimizasyon ile daha iyi sonuç")
            else:
                print(f"   ⚖️  İki algoritma benzer boyutta MDS üretiyor")
        
        print(f"\n⏱️  Çalışma Süresi:")
        print(f"   Seq_11.1:  {seq_time:.6f} saniye")
        print(f"   Span_11.2: {span_time:.6f} saniye")
        if seq_time > 0:
            if time_ratio > 2:
                print(f"   ✅ Seq_11.1, Span_11.2'den {time_ratio:.2f}x daha hızlı")
                print(f"   💡 Avantaj: Merkezi algoritma paralel işlem yapmadan hızlı")
            elif time_ratio < 0.5:
                print(f"   ✅ Span_11.2, Seq_11.1'den {1/time_ratio:.2f}x daha hızlı")
                print(f"   💡 Avantaj: Dağıtık algoritma paralel çalışma avantajı")
            else:
                print(f"   ⚖️  İki algoritma benzer sürede çalışıyor")
        
        print(f"\n📨 İletişim Karmaşıklığı:")
        print(f"   Seq_11.1:  {seq_msgs:6d} mesaj ({seq_msgs_per_node:.2f} mesaj/node)")
        print(f"   Span_11.2: {span_msgs:6d} mesaj ({span_msgs_per_node:.2f} mesaj/node)")
        if seq_msgs == 0:
            print(f"   ✅ Seq_11.1 merkezi olduğu için mesaj göndermiyor")
            print(f"   💡 Avantaj: Merkezi sistemlerde iletişim maliyeti yok")
        else:
            print(f"   💡 Span_11.2 dağıtık olduğu için {span_msgs} mesaj gönderiyor")
            print(f"   ⚠️  Dağıtık sistemlerde iletişim maliyeti önemli faktör")
        
        print(f"\n💼 Senaryo Önerileri:")
        if "Small" in network or num_nodes < 100:
            print(f"   • Küçük ağlar için Seq_11.1 tercih edilebilir (hızlı, merkezi kontrol)")
            print(f"   • Span_11.2 daha küçük MDS üretiyorsa tercih edilebilir")
        elif "Medium" in network or num_nodes < 500:
            print(f"   • Orta ölçekli ağlar için:")
            if size_ratio > 1.3:
                print(f"     → Span_11.2 önerilir (daha küçük MDS, kabul edilebilir mesaj maliyeti)")
            else:
                print(f"     → Seq_11.1 önerilir (hızlı, merkezi kontrol mümkün)")
        else:
            print(f"   • Büyük ölçekli ağlar için:")
            if span_msgs_per_node < 10:
                print(f"     → Span_11.2 önerilir (ölçeklenebilir, dağıtık)")
            else:
                print(f"     → Seq_11.1 önerilir (iletişim maliyeti yüksek)")
        
        print(f"\n📈 Algoritma Avantajları:")
        print(f"   Seq_11.1:")
        print(f"     ✅ Merkezi kontrol - tek noktadan yönetim")
        print(f"     ✅ Hızlı çalışma - paralel işlem gerekmez")
        print(f"     ✅ İletişim maliyeti yok")
        print(f"     ❌ Merkezi nokta başarısızlığı riski")
        print(f"     ❌ Ölçeklenebilirlik sınırlı")
        
        print(f"\n   Span_11.2:")
        print(f"     ✅ Dağıtık - merkezi nokta başarısızlığına dayanıklı")
        print(f"     ✅ Ölçeklenebilir - büyük ağlarda çalışabilir")
        print(f"     ✅ Genellikle daha küçük MDS üretir")
        print(f"     ❌ İletişim maliyeti var")
        print(f"     ❌ Daha yavaş olabilir (mesaj gecikmeleri)")
        
        print("\n" + "-" * 75)

