"""
QoS Priority Controller - POX OpenFlow Controller
Prioritizes traffic based on UDP port numbers:
  - Port 5001 = High Priority (Video/VOIP)
  - Port 5002 = Low Priority  (Bulk Transfer)
"""

from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.packet.udp import udp

log = core.getLogger()

HIGH_PRIORITY = 200
LOW_PRIORITY  = 100
DEFAULT_PRIORITY = 50

HIGH_PRIORITY_PORT = 5001
LOW_PRIORITY_PORT  = 5002

class QoSController(object):

    def __init__(self, connection):
        self.connection = connection
        self.mac_to_port = {}
        connection.addListeners(self)
        log.info("QoS Controller connected to switch: %s" % dpidToStr(connection.dpid))
        self.install_qos_rules()

    def install_qos_rules(self):

        # HIGH Priority Rule - UDP port 5001
        msg = of.ofp_flow_mod()
        msg.priority = HIGH_PRIORITY
        msg.match.dl_type = 0x0800
        msg.match.nw_proto = 17
        msg.match.tp_dst = HIGH_PRIORITY_PORT
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        self.connection.send(msg)
        log.info("Installed HIGH priority rule for UDP port %d" % HIGH_PRIORITY_PORT)

        # LOW Priority Rule - UDP port 5002
        msg = of.ofp_flow_mod()
        msg.priority = LOW_PRIORITY
        msg.match.dl_type = 0x0800
        msg.match.nw_proto = 17
        msg.match.tp_dst = LOW_PRIORITY_PORT
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        self.connection.send(msg)
        log.info("Installed LOW priority rule for UDP port %d" % LOW_PRIORITY_PORT)

        log.info("QoS rules installed successfully on switch %s" % dpidToStr(self.connection.dpid))

    def _handle_PacketIn(self, event):

        packet = event.parsed
        if not packet.parsed:
            log.warning("Incomplete packet, ignoring")
            return

        self.mac_to_port[packet.src] = event.port

        ip_packet = packet.find('ipv4')
        if ip_packet:
            udp_packet = packet.find('udp')
            if udp_packet:
                dst_port = udp_packet.dstport
                if dst_port == HIGH_PRIORITY_PORT:
                    log.info("HIGH PRIORITY traffic detected | %s -> %s | UDP port %d"
                             % (packet.src, packet.dst, dst_port))
                elif dst_port == LOW_PRIORITY_PORT:
                    log.info("LOW PRIORITY traffic detected  | %s -> %s | UDP port %d"
                             % (packet.src, packet.dst, dst_port))

        if packet.dst in self.mac_to_port:
            out_port = self.mac_to_port[packet.dst]
        else:
            out_port = of.OFPP_FLOOD

        if out_port != of.OFPP_FLOOD:
            msg = of.ofp_flow_mod()
            msg.priority = DEFAULT_PRIORITY
            msg.match = of.ofp_match.from_packet(packet, event.port)
            msg.idle_timeout = 30
            msg.hard_timeout = 120
            msg.actions.append(of.ofp_action_output(port=out_port))
            msg.data = event.ofp
            self.connection.send(msg)
        else:
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = event.port
            self.connection.send(msg)


class QoSLaunch(object):

    def __init__(self):
        core.openflow.addListeners(self)
        log.info("QoS Controller started. Waiting for switches...")

    def _handle_ConnectionUp(self, event):
        log.info("Switch connected: %s" % dpidToStr(event.dpid))
        QoSController(event.connection)


def launch():
    core.registerNew(QoSLaunch)
    log.info("QoS Priority Controller launched!")
