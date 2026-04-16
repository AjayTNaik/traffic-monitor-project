# Traffic Monitoring and Statistics Collector

## Objective
Build a controller module that collects and displays traffic statistics using Mininet and POX controller.

## Tools Used
- Mininet
- POX Controller
- Open vSwitch
- Python
- iperf

## Files
- topo.py
- monitor.py

## Topology
1 switch (s1), 3 hosts (h1, h2, h3)

## How to Run

### Run Controller
```bash
cd ~/pox
python3 pox.py openflow.of_01 --port=6633 ../traffic_project/monitor.py
