"""
Assignent 3: Packet Filtering in Software Defined Networks
Computer Networks
Alan Licerio and Joshua Ramos
Last Modified on: 04-16-22
"""
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr
import pox.lib.packet as pkt

log = core.getLogger()

#statically allocate a routing table for hosts
#MACs used in only in part 4
# hnotrust1: untrusted host.
IPS = {
  "h10" : ("10.0.1.10", '00:00:00:00:00:01'),
  "h20" : ("10.0.2.20", '00:00:00:00:00:02'),
  "h30" : ("10.0.3.30", '00:00:00:00:00:03'),
  "serv1" : ("10.0.4.10", '00:00:00:00:00:04'),
  "hnotrust1" : ("172.16.10.100", '00:00:00:00:00:05'), 
}

class Part3Controller (object):
  """
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    print (connection.dpid)
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)
    #use the dpid to figure out what switch is being created
    if (connection.dpid == 1):
      self.s1_setup()
    elif (connection.dpid == 2):
      self.s2_setup()
    elif (connection.dpid == 3):
      self.s3_setup()
    elif (connection.dpid == 21):
      self.cores21_setup()
    elif (connection.dpid == 31):
      self.dcs31_setup()
    else:
      print ("UNKNOWN SWITCH")
      exit(1)

  def s1_setup(self):
    self.send_packets()

  def s2_setup(self):
    self.send_packets()

  def s3_setup(self):
    self.send_packets()

  def cores21_setup(self):
    self.send_packets()
    self.block_s1()
    self.block_icmp()
    self.regular_traffic()

  def dcs31_setup(self):
    self.send_packets()


  #used in part 4 to handle individual ARP packets
  #not needed for part 3 (USE RULES!)
  #causes the switch to output packet_in on out_port
  def resend_packet(self, packet_in, out_port):
    msg = of.ofp_packet_out()
    msg.data = packet_in
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)
    self.connection.send(msg)

  def _handle_PacketIn (self, event):
    """
    Packets not handled by the router rules will be
    forwarded to this method to be handled by the controller
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    print ("Unhandled packet from " + str(self.connection.dpid) + ":" + packet.dump())


  def send_packets(self, action=of.ofp_action_output(port=of.OFPP_FLOOD)):
    """
    Only sends packets that are going thorugh the network. Packets outside it are blocked.
    """
    self.connection.send(of.ofp_flow_mod(action=action, priority=2))

    # Drop outisder packets
    self.connection.send(of.ofp_flow_mod(priority=1))

  def block_s1(self, block=IPS["hnotrust1"][0]):
    """
    Blocks all traffic from the untrusted host (hnotrust1) to S1
    """
    block = of.ofp_flow_mod(priority=19, match=of.ofp_match(dl_type=0x800, nw_src=block, nw_dst=IPS["serv1"][0]))
    self.connection.send(block)

  # Blocks all ICMP traffic
  def block_icmp(self, block=IPS["hnotrust1"][0]):
    """
    Blockage to prevent the internet from discovering internal IP. 
    Blocks all ICMP traffic from hnotrust
    """
    block = of.ofp_flow_mod(priority=20, match=of.ofp_match(dl_type=0x800, nw_src=block, nw_proto=pkt.ipv4.ICMP_PROTOCOL))
    self.connection.send(block)
  
  def regular_traffic(self):
    """
    Manages the regular traffic between hosts. 
    """
    hosts = {
      1: (IPS["h10"][0],1),
      2: (IPS["h20"][0],2),
      3: (IPS["h30"][0],3),
      4: (IPS["serv1"][0],4),
      5: (IPS["hnotrust1"][0],5)
    }

    for i in range(len(hosts)):
      host = hosts[i+1][0]
      port = hosts[i+1][1]

      self.connection.send(of.ofp_flow_mod(action=of.ofp_action_output(port=port), priority=5,
      match=of.ofp_match(dl_type=0x800, nw_dst=host)))


def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Part3Controller(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
