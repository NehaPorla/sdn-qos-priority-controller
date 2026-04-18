"""
Mininet Topology for QoS Priority Controller
4 hosts connected to 1 switch controlled by POX
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def create_topology():

    setLogLevel('info')

    net = Mininet(
        switch=OVSSwitch,
        controller=RemoteController,
        link=TCLink,
        autoSetMacs=True
    )

    info("*** Creating Controller\n")
    controller = net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6633
    )

    info("*** Creating Switch\n")
    s1 = net.addSwitch('s1', protocols='OpenFlow10')

    info("*** Creating Hosts\n")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')

    info("*** Creating Links\n")
    net.addLink(h1, s1, bw=10, delay='10ms')
    net.addLink(h2, s1, bw=10, delay='10ms')
    net.addLink(h3, s1, bw=10, delay='10ms')
    net.addLink(h4, s1, bw=10, delay='10ms')

    info("*** Starting Network\n")
    net.start()

    s1.cmd('ovs-vsctl set bridge s1 protocols=OpenFlow10')

    info("*** Network Ready!\n")

    CLI(net)

    info("*** Stopping Network\n")
    net.stop()

if __name__ == '__main__':
    create_topology()
