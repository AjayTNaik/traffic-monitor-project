from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer

log = core.getLogger()

def request_stats():
    for connection in core.openflow.connections:
        connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
        connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
    log.info("Requested switch statistics")

def flow_stats(event):
    log.info("Flow Stats Received")
    for stat in event.stats:
        log.info("Packets=%s Bytes=%s", stat.packet_count, stat.byte_count)

def port_stats(event):
    log.info("Port Stats Received")
    for stat in event.stats:
        log.info("Port %s RX=%s TX=%s",
                 stat.port_no, stat.rx_packets, stat.tx_packets)

def launch():
    core.openflow.addListenerByName("FlowStatsReceived", flow_stats)
    core.openflow.addListenerByName("PortStatsReceived", port_stats)

    Timer(10, request_stats, recurring=True)

    log.info("Traffic Monitor Started")
