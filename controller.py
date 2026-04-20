from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.recoco import Timer
import time
import json

log = core.getLogger()

class FinalController(object):

    def __init__(self):
        self.mac_table = {}
        self.connections = []

        # 🔥 Store previous stats for rate calculation
        self.prev_stats = {}

        core.openflow.addListeners(self)

        log.info("🚀 Final SDN Controller Started (Full Features)")

        Timer(5, self._request_stats, recurring=True)

    # 🔌 Switch connected
    def _handle_ConnectionUp(self, event):
        dpid = event.dpid
        self.mac_table[dpid] = {}
        self.connections.append(event.connection)

        log.info("🔗 Switch connected: %s", dpid_to_str(dpid))

    # 🔌 Switch disconnected
    def _handle_ConnectionDown(self, event):
        if event.connection in self.connections:
            self.connections.remove(event.connection)

    # =============================
    # 🚀 FORWARDING
    # =============================
    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            return

        dpid = event.dpid
        in_port = event.port

        src = packet.src
        dst = packet.dst

        self.mac_table.setdefault(dpid, {})
        self.mac_table[dpid][src] = in_port

        if dst in self.mac_table[dpid]:
            out_port = self.mac_table[dpid][dst]
        else:
            out_port = of.OFPP_FLOOD

        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.actions.append(of.ofp_action_output(port=out_port))
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        event.connection.send(msg)

        out = of.ofp_packet_out()
        out.data = event.ofp
        out.in_port = in_port
        out.actions.append(of.ofp_action_output(port=out_port))
        event.connection.send(out)

    # =============================
    # 📊 REQUEST STATS
    # =============================
    def _request_stats(self):
        for conn in self.connections:
            req = of.ofp_stats_request(body=of.ofp_flow_stats_request())
            conn.send(req)

    # =============================
    # 📊 PROCESS STATS + RATE + JSON
    # =============================
    def _handle_FlowStatsReceived(self, event):
        dpid = dpid_to_str(event.connection.dpid)

        report = {
            "timestamp": time.strftime('%H:%M:%S'),
            "switch": dpid,
            "flows": [],
            "summary": {
                "total_flows": 0,
                "total_packets": 0,
                "total_bytes": 0
            }
        }

        for stat in event.stats:

            if stat.priority == 0:
                continue

            match = stat.match

            dl_type = getattr(match, 'dl_type', None)
            if dl_type != 0x800:
                continue

            src = str(getattr(match, 'nw_src', 'N/A'))
            dst = str(getattr(match, 'nw_dst', 'N/A'))

            proto_num = getattr(match, 'nw_proto', None)

            # 🔥 Protocol detection
            if proto_num == 1:
                proto = "ICMP"
            elif proto_num == 6:
                proto = "TCP"
            elif proto_num == 17:
                proto = "UDP"
            else:
                proto = "OTHER"

            packets = stat.packet_count
            bytes_ = stat.byte_count

            # 🔥 UNIQUE KEY for each flow
            key = (dpid, src, dst, proto)

            prev_packets, prev_bytes = self.prev_stats.get(key, (0, 0))

            # 🔥 RATE CALCULATION (per 5 sec interval)
            packet_rate = (packets - prev_packets) / 5.0
            byte_rate = (bytes_ - prev_bytes) / 5.0

            # Save current stats
            self.prev_stats[key] = (packets, bytes_)

            flow_data = {
                "src": src,
                "dst": dst,
                "protocol": proto,
                "packets": packets,
                "bytes": bytes_,
                "packet_rate": round(packet_rate, 2),
                "byte_rate": round(byte_rate, 2)
            }

            report["flows"].append(flow_data)

            report["summary"]["total_flows"] += 1
            report["summary"]["total_packets"] += packets
            report["summary"]["total_bytes"] += bytes_

        # 🔥 PRINT CLEAN OUTPUT
        print("\n📊 ===== TRAFFIC REPORT =====")
        print(f"⏱ Time:   {report['timestamp']}")
        print(f"🔌 Switch: {dpid}")

        for flow in report["flows"]:
            print(f"➡️ {flow['src']} → {flow['dst']} ({flow['protocol']})")
            print(f"   Packets: {flow['packets']} | Bytes: {flow['bytes']}")
            print(f"   Rate: {flow['packet_rate']} pkt/s | {flow['byte_rate']} B/s")

        print("------------ SUMMARY ------------")
        print(f"📈 Flows:   {report['summary']['total_flows']}")
        print(f"📦 Packets: {report['summary']['total_packets']}")
        print(f"💾 Bytes:   {report['summary']['total_bytes']}")
        print("================================\n")

        # 🔥 JSON OUTPUT
        print("📄 JSON REPORT:")
        print(json.dumps(report, indent=4))

        # 💾 SAVE FILE
        with open("traffic_report.json", "a") as f:
            f.write(json.dumps(report) + "\n")


def launch():
    core.registerNew(FinalController)
