"""
Assignent 3: Packet Filtering in Software Defined Networks
Computer Networks
Alan Licerio and Joshua Ramos
Last Modified on: 04-16-22
"""

#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

class part1_topo(Topo):
    """
    Builds a small topology. Each host is connected to the same switch (s1)
    """
    def build(self):
        switch1 = self.addSwitch('s1', protocols='OpenFlow13')
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        host3 = self.addHost('h3')
        host4 = self.addHost('h4')
        
        self.addLink(host1,switch1)
        self.addLink(host2,switch1)
        self.addLink(host3,switch1)
        self.addLink(host4,switch1)
	
topos = {'part1' : part1_topo}

if __name__ == '__main__':
    t = part1_topo()
    net = Mininet (topo=t)
    net.start()
    CLI(net)
    net.stop()
