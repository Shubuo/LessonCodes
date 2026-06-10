# Distributed & Advanced Networks Course Projects

This repository contains the source codes, simulation scripts, results, and academic reports for the **Distributed Algorithms** and **Advanced Networks** PhD coursework.

The repository is structured into two main projects:

## 1. [Project 1: Distributed Algorithms - Minimum Dominating Set (MDS) Simulation](./Project1-DistributedAlgorithms-MDS-Simulation)
This project models and simulates the Minimum Dominating Set (MDS) problem in Mobile Ad Hoc Networks (MANETs). 
- Implements distributed algorithms to find dominating sets.
- Simulates node mobility using random waypoint models.
- Provides comprehensive Python-based visualizations and performance metrics.

## 2. [Project 2: Advanced Networks - SDN-based UAV Edge Priority Slicing](./Project2-AdvancedNetworks-SDN-UAV-Slicing)
This project implements an SDN-assisted priority slicing architecture for UAV-to-Edge communication networks.
- Built on top of **Mininet** and **Open vSwitch (OVS)**.
- Uses `tc qdisc` (Traffic Control) to enforce bandwidth isolation (Priority Slicing) on bottleneck links.
- Includes a terminal-based CLI demo and an interactive web-based monitoring dashboard.
- Contains the final IEEE-formatted academic report detailing the system architecture, Scenario A (Routing) and Scenario B (Priority Slicing).

### Repository Structure

```text
.
├── Project1-DistributedAlgorithms-MDS-Simulation/
│   ├── algorithms.py
│   ├── distsim.py
│   ├── mobility.py
│   ├── project-mds.py
│   ├── visualization.py
│   ├── conference_101719.tex / .pdf  (MDS Project Report)
│   └── results/                      (Simulation outputs and charts)
│
├── Project2-AdvancedNetworks-SDN-UAV-Slicing/
│   ├── src/                          (Mininet simulation scripts, web dashboard, and CLI demo)
│   ├── Final-Report.tex / .pdf       (SDN Slicing Project Report)
│   └── README.md                     (Detailed documentation for the Mininet project)
│
└── README.md                         (This file)
```
