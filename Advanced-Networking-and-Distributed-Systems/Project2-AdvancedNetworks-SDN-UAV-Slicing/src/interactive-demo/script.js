// DOM Elements
const btnBestEffort = document.getElementById('btn-besteffort');
const btnSdn = document.getElementById('btn-sdn');
const btnToggleBg = document.getElementById('btn-toggle-bg');
const btnSnapshot = document.getElementById('btn-snapshot');

const valBw = document.getElementById('val-bw');
const valDelay = document.getElementById('val-delay');
const valQueue = document.getElementById('val-queue');
const inputBw = document.getElementById('input-bw');
const inputDelay = document.getElementById('input-delay');
const inputQueue = document.getElementById('input-queue');
const canvasBw = document.getElementById('canvas-bw');

const metricH1 = document.getElementById('metric-h1-throughput');
const metricH3 = document.getElementById('metric-h3-throughput');
const barH1 = document.getElementById('bar-h1');
const barH3 = document.getElementById('bar-h3');
const statusH3 = document.getElementById('status-h3');
const sdnShield = document.getElementById('sdn-shield');
const packetLayer = document.getElementById('packet-layer');
const logTbody = document.getElementById('log-tbody');

// State
let sdnActive = false;
let bgActive = false;
let bw = 10;
let delay = 20;
let queue = 20;

let currentH1 = 0;
let currentH3 = 0;
let targetH1 = 0;
let targetH3 = 0;

let animationFrameId;
let activePackets = [];

const nodes = {
    h1: {x: 15, y: 20}, h3: {x: 15, y: 80},
    s1: {x: 40, y: 50}, s2: {x: 60, y: 50},
    h2: {x: 85, y: 20}, h4: {x: 85, y: 80}
};

// Math Model for Simulation
function calculateThroughput() {
    const uavDemand = 10; // UAV wants 10 Mbps
    const bgDemand = 50;  // BG wants 50 Mbps
    const actualBgDemand = bgActive ? bgDemand : 0;
    const totalDemand = uavDemand + actualBgDemand;

    // Delay penalty (simple model: higher delay = slightly lower TCP throughput)
    const delayPenalty = 100 / (100 + delay * 0.5); 

    if (sdnActive) {
        // SDN QoS Limits BG traffic to max 2 Mbps at the switch
        const bgAllowed = Math.min(2, bw);
        const uavAllowed = bw - bgAllowed;
        
        targetBg = bgActive ? Math.min(bgDemand, bgAllowed) : 0;
        targetUav = Math.min(uavDemand, uavAllowed) * delayPenalty;
    } else {
        // Best Effort: Proportional sharing if congested
        if (totalDemand <= bw) {
            targetUav = uavDemand * delayPenalty;
            targetBg = actualBgDemand;
        } else {
            targetUav = uavDemand * (bw / totalDemand) * delayPenalty;
            targetBg = actualBgDemand * (bw / totalDemand);
        }
    }

    targetH1 = Math.max(0, targetUav);
    targetH3 = Math.max(0, targetBg);
}

// UI Updates
function updateUI() {
    btnBestEffort.classList.toggle('active', !sdnActive);
    btnSdn.classList.toggle('active', sdnActive);
    sdnShield.classList.toggle('hidden', !sdnActive);
    
    if (bgActive) {
        btnToggleBg.innerText = "Traffic ON";
        btnToggleBg.classList.replace('btn-primary', 'btn-warning');
        statusH3.classList.add('active-bg');
    } else {
        btnToggleBg.innerText = "Traffic OFF";
        btnToggleBg.classList.replace('btn-warning', 'btn-primary');
        statusH3.classList.remove('active-bg');
    }

    valBw.innerText = bw;
    canvasBw.innerText = bw;
    valDelay.innerText = delay;
    valQueue.innerText = queue;

    calculateThroughput();
}

// Animation Loop for metrics
setInterval(() => {
    currentH1 += (targetH1 - currentH1) * 0.1;
    currentH3 += (targetH3 - currentH3) * 0.1;
    
    metricH1.innerText = currentH1.toFixed(2);
    metricH3.innerText = currentH3.toFixed(2);
    
    barH1.style.width = Math.min((currentH1 / 10) * 100, 100) + '%';
    barH3.style.width = Math.min((currentH3 / 50) * 100, 100) + '%';
}, 50);

// Packet Animation Engine
function createPacket(type, source, dropProb, dropS1Prob) {
    const el = document.createElement('div');
    el.classList.add('packet', type);
    packetLayer.appendChild(el);

    const packet = {
        el, type, progress: 0,
        path: [nodes[source], nodes.s1, nodes.s2, type === 'tcp' ? nodes.h2 : nodes.h4],
        dropAt: -1,
        speed: type === 'tcp' ? 0.02 : 0.03
    };

    if (Math.random() < dropS1Prob) {
        packet.dropAt = 0.9 + Math.random() * 0.1; // Drop at S1
    } else if (Math.random() < dropProb) {
        packet.dropAt = 1.2 + Math.random() * 0.6; // Drop in bottleneck
    }

    activePackets.push(packet);
}

function getPixelCoords(percentPos) {
    const rect = packetLayer.getBoundingClientRect();
    return { x: (percentPos.x / 100) * rect.width, y: (percentPos.y / 100) * rect.height };
}

function animatePackets() {
    // Generate packets
    let uavDrop = 0;
    let bgDrop = 0;
    let bgDropS1 = 0;

    if (sdnActive) {
        uavDrop = Math.max(0, 1 - (targetH1 / 10)); 
        bgDrop = bgActive ? (targetH3 / 50 > 0 ? 0.1 : 0) : 0;
        bgDropS1 = bgActive ? 0.95 : 0; // Huge drop at S1 due to SDN
    } else {
        const total = 10 + (bgActive ? 50 : 0);
        const dropRate = bw < total ? 1 - (bw / total) : 0;
        uavDrop = dropRate;
        bgDrop = dropRate;
    }

    if (Math.random() < 0.15) createPacket('tcp', 'h1', uavDrop, 0);
    if (bgActive && Math.random() < 0.4) createPacket('udp', 'h3', bgDrop, bgDropS1);

    for (let i = activePackets.length - 1; i >= 0; i--) {
        const p = activePackets[i];
        p.progress += p.speed;

        if (p.dropAt !== -1 && p.progress >= p.dropAt) {
            p.el.classList.add('dropped');
            activePackets.splice(i, 1);
            setTimeout(() => p.el.remove(), 300);
            continue;
        }
        if (p.progress >= 3) {
            p.el.remove();
            activePackets.splice(i, 1);
            continue;
        }

        const segment = Math.floor(p.progress);
        const segmentProgress = p.progress - segment;
        const start = getPixelCoords(p.path[segment]);
        const end = getPixelCoords(p.path[segment + 1]);
        
        const x = start.x + (end.x - start.x) * segmentProgress;
        const y = start.y + (end.y - start.y) * segmentProgress;

        if (segment === 1) p.progress -= p.speed * 0.6; // Slow down in bottleneck

        p.el.style.left = x + 'px';
        p.el.style.top = y + 'px';
    }
    animationFrameId = requestAnimationFrame(animatePackets);
}

// Event Listeners
btnBestEffort.addEventListener('click', () => { sdnActive = false; updateUI(); });
btnSdn.addEventListener('click', () => { sdnActive = true; updateUI(); });
btnToggleBg.addEventListener('click', () => { bgActive = !bgActive; updateUI(); });

inputBw.addEventListener('input', (e) => { bw = parseInt(e.target.value); updateUI(); });
inputDelay.addEventListener('input', (e) => { delay = parseInt(e.target.value); updateUI(); });
inputQueue.addEventListener('input', (e) => { queue = parseInt(e.target.value); updateUI(); });

btnSnapshot.addEventListener('click', () => {
    const time = new Date().toLocaleTimeString();
    const stateStr = sdnActive ? '<span class="log-state-sdn">SDN Slicing</span>' : '<span class="log-state-best">Best Effort</span>';
    const bgStr = bgActive ? 'ON' : 'OFF';
    
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>${time}</td>
        <td>${stateStr}</td>
        <td>${bgStr}</td>
        <td>${bw}</td>
        <td>${delay}</td>
        <td>${queue}</td>
        <td class="log-uav">${currentH1.toFixed(2)}</td>
        <td class="log-udp">${currentH3.toFixed(2)}</td>
    `;
    logTbody.insertBefore(tr, logTbody.firstChild);
});

// Init
updateUI();
animatePackets();

window.addEventListener('resize', () => {
    activePackets.forEach(p => p.el.remove());
    activePackets = [];
});
