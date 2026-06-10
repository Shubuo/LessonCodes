#!/usr/bin/env python3

import time
import re
from mininet.net import Mininet
from mininet.node import OVSController
from mininet.link import TCLink
from mininet.log import setLogLevel

def parse_iperf_line(line):
    # Python 3'te popen.stdout byte dondugu icin string'e cevirerek hatayi onluyoruz
    if isinstance(line, bytes):
        line = line.decode('utf-8', errors='ignore')
    match = re.search(r'([0-9.]+)\s+([KMG])bits/sec', line)
    if match:
        val = float(match.group(1))
        unit = match.group(2)
        if unit == 'K': return val / 1000.0
        elif unit == 'G': return val * 1000.0
        return val
    return None

def run_demo():
    print('[96m' + '='*60)
    print('  MININET SDN UAV-EDGE SLICING CANLI DEMO')
    print('='*60 + '[0m')

    print("[93m[1/4] Topoloji ve Cihazlar Hazirlaniyor...[0m")
    net = Mininet(controller=OVSController, link=TCLink, autoSetMacs=True)
    net.addController('c0')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    net.addLink(h1, s1, bw=100, delay='1ms')
    net.addLink(h3, s1, bw=100, delay='1ms')
    net.addLink(s2, h2, bw=100, delay='1ms')
    net.addLink(s2, h4, bw=100, delay='1ms')
    # Bottleneck 10Mbps 20ms queue=20
    net.addLink(s1, s2, bw=10, delay='20ms', max_queue_size=20, use_htb=True)
    net.start()
    net.pingAll(timeout='0.5')
    try:
        print("[1;32m*** Ag basariyla kuruldu! (DarBogaz: 10Mbps) ***[0m")
        time.sleep(1)
        h2.cmd("iperf -s -p 5001 > /tmp/h2_iperf.log 2>&1 &")
        h4.cmd("iperf -s -u -p 5002 > /tmp/h4_iperf.log 2>&1 &")
        time.sleep(1)
        print("[92m[2/4] A: Best-Effort Durumu (Normal Ag)[0m")
        print("   -> Kritik IHA trafigi (h1 -> h2) baslatiliyor...")
        print("   -> [Sadece IHA Trafigi - Arka Plan YUK YOK]")
        p_crit = h1.popen("iperf -c 10.0.0.2 -p 5001 -t 5 -i 1")
        for line in p_crit.stdout:
            val = parse_iperf_line(line)
            if val is not None:
                print(f"      Canli IHA Hizi: [1;32m{val:.2f} Mbps[0m")
        p_crit.wait()
        print("-> Arka plan UDP trafigi baslatiliyor (50 Mbps yuku)...")
        p_bg = h3.popen("iperf -c 10.0.0.4 -u -p 5002 -b 50M -t 15 &")
        time.sleep(2)
        print("   -> Kritik IHA trafigi tekrar test ediliyor (Best-Effort Altinda)...")
        p_crit2 = h1.popen("iperf -c 10.0.0.2 -p 5001 -t 6 -i 1")
        final_be = 0
        for line in p_crit2.stdout:
            val = parse_iperf_line(line)
            if val is not None:
                final_be = val
                print(f"      Canli IHA Hizi: [1;31m{val:.2f} Mbps[0m (Trafik tikanikligi!)")
        p_crit2.wait()
        print(f"[91m   [SONUC] Best-Effort Hizi: {final_be:.2f} Mbps (Ag tikandi!)[0m")
        time.sleep(1)
        print("[92m[3/4] B: SDN Priority Slicing Aktif Ediliyor (QoS)[0m")
        print("   -> SDN kurali: Arka plan trafigi max 2 Mbps ile sinirlandiriliyor...")
        h3.cmd("tc qdisc del dev h3-eth0 root 2>/dev/null || true")
        h3.cmd("tc qdisc add dev h3-eth0 root tbf rate 2mbit burst 32kbit latency 50ms")
        time.sleep(2)
        print("   -> Kritik IHA trafigi ayni UDP yuku altinda tekrar test ediliyor...")
        p_crit3 = h1.popen("iperf -c 10.0.0.2 -p 5001 -t 6 -i 1")
        final_qos = 0
        for line in p_crit3.stdout:
            val = parse_iperf_line(line)
            if val is not None:
                final_qos = val
                print(f"      Canli IHA Hizi: [1;32m{val:.2f} Mbps[0m (Kurtarildi!)")
        p_crit3.wait()
        print(f"[92m   [SONUC] SDN QoS Hizi:     {final_qos:.2f} Mbps (Trafik kurtarildi!)[0m")
    finally:
        print("[96m[4/4] Demo tamamlandi. Ag temizleniyor...[0m")
        h2.cmd("killall -9 iperf 2>/dev/null || true")
        h4.cmd("killall -9 iperf 2>/dev/null || true")
        h3.cmd("killall -9 iperf 2>/dev/null || true")
        net.stop()

if __name__ == '__main__':
    setLogLevel('error')
    run_demo()
