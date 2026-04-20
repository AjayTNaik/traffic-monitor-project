# Final SDN Controller with Traffic Monitoring

This project implements a **POX-based SDN controller** that performs basic packet forwarding and also monitors live network traffic using OpenFlow flow statistics.

The controller learns MAC addresses, installs forwarding rules, requests flow statistics every 5 seconds, classifies traffic by protocol, calculates packet/byte rates, prints readable traffic reports, and stores reports in a JSON file.

## Features

- **MAC learning switch behavior**
  - Learns source MAC addresses and their incoming ports.
  - For known destinations, forwards packets to the correct port.
  - For unknown destinations, floods the packet.

- **Automatic flow rule installation**
  - Installs flow entries using `ofp_flow_mod`.
  - Uses:
    - `idle_timeout = 10`
    - `hard_timeout = 30`

- **Periodic traffic monitoring**
  - Requests flow statistics from connected switches every **5 seconds**.

- **Protocol detection**
  - Identifies IPv4 traffic and labels flows as:
    - **ICMP**
    - **TCP**
    - **UDP**
    - **OTHER**

- **Traffic rate calculation**
  - Computes:
    - **packet rate (pkt/s)**
    - **byte rate (B/s)**
  - Uses previous flow statistics to calculate rate over each 5-second interval.

- **Readable console reports**
  - Prints traffic information in a clean format with:
    - timestamp
    - switch ID
    - source and destination IPs
    - protocol
    - packets and bytes
    - packet and byte rates
    - overall summary

- **JSON report generation**
  - Appends each traffic snapshot to `traffic_report.json`.

## Files

### `final_controller.py`
Main SDN controller file.

It handles:
- switch connection and disconnection
- packet forwarding
- stats requests
- flow statistics processing
- JSON report writing

### `traffic_report.json`
Output file containing traffic snapshots collected from the controller.

Each entry stores:
- timestamp
- switch ID
- flow list
- per-flow packet and byte counts
- protocol
- packet rate and byte rate
- overall summary

## How the Controller Works

### 1. Switch connection
When a switch connects, the controller:
- stores the switch connection
- initializes a MAC table for that switch

### 2. Packet forwarding
When a packet arrives:
- the controller reads source and destination MAC addresses
- learns the source MAC and incoming port
- checks whether destination MAC is already known
  - if known → forwards to that port
  - if unknown → floods the packet
- installs a flow rule for future packets

### 3. Statistics collection
Every 5 seconds, the controller sends a flow stats request to all connected switches.

### 4. Flow processing
For each received flow entry:
- ignores default priority flows
- accepts only IPv4 flows
- extracts source IP and destination IP
- detects protocol number
- reads packet and byte counters
- calculates packet rate and byte rate
- creates a report entry

### 5. Report generation
The controller:
- prints a readable traffic summary in the terminal
- converts the same data to JSON
- appends it to `traffic_report.json`

## Example Traffic Seen in the Report

Based on the generated report file, the controller captured multiple traffic types:

- **TCP traffic** between `10.0.0.1` and `10.0.0.2`
- **ICMP traffic** between `10.0.0.1` and `10.0.0.2`
- **UDP traffic** between `10.0.0.1` and `10.0.0.2`
- reports from switches:
  - `00-00-00-00-00-01`
  - `00-00-00-00-00-02`
  - `00-00-00-00-00-03`

Some report entries show active traffic, while some show empty flow lists when no monitored flow is present at that time.

## Requirements

To run this project, you typically need:

- Python
- POX controller framework
- OpenFlow 1.0 compatible setup
- Mininet or an SDN testbed with OpenFlow switches

## Running the Controller

A typical way to run the controller in POX is:

```bash
./pox.py log.level --DEBUG misc.final_controller
```

> Make sure `final_controller.py` is placed where POX can import it correctly.

## Output Format

### Console output
The controller prints traffic in a readable format like:

```text
📊 ===== TRAFFIC REPORT =====
⏱ Time:   HH:MM:SS
🔌 Switch: 00-00-00-00-00-01
➡️ 10.0.0.1 → 10.0.0.2 (TCP)
   Packets: ... | Bytes: ...
   Rate: ... pkt/s | ... B/s
------------ SUMMARY ------------
📈 Flows:   ...
📦 Packets: ...
💾 Bytes:   ...
================================
```

### JSON output
Each line in `traffic_report.json` is a JSON object containing one traffic snapshot.

## Notes

- The controller stores previous flow counters in `prev_stats` to calculate rates.
- If counters reset or a new flow appears, rate values may briefly become zero or negative depending on the difference between old and new values.
- Only IPv4 flows are processed for protocol classification.
- Default priority flows are skipped.

## Project Summary

In simple words, this project is a **smart SDN controller** that does two things:

1. **forwards packets like a learning switch**
2. **monitors network traffic and saves reports automatically**

So it is not just routing packets — it is also acting like a small traffic analysis system for an SDN network.
