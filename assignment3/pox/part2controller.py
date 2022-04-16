from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Firewall (object):
  """
  A Firewall object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

    # Switch Rules:
    # IPv4 icmp
    connection.send(of.ofp_flow_mod(action=of.ofp_action_output(port=of.OFPP_FLOOD),
					priority=2, match=of.ofp_match(dl_type=0x0800, nw_proto=1)))
    # Any arp
    connection.send(of.ofp_flow_mod(action=of.ofp_action_output(port=of.OFPP_FLOOD),
    		    			priority=1, match=of.ofp_match(dl_type=0x0806)))
    # Drop other IPv4	    			
    self.connection.send(of.ofp_flow_mod(action=of.ofp_action_output(port=of.OFPP_NONE),
					priority=0, match=of.ofp_match(dl_type=0x0800)))
    
    # Drop non-arp IPv6				
    self.connection.send(of.ofp_flow_mod(action=of.ofp_action_output(port=of.OFPP_NONE),
					priority=0, match=of.ofp_match(dl_type=0x86dd)))
					
    

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
    print ("Unhandled packet :" + str(packet.dump()))

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Firewall(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
