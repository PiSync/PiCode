"""slave.py: Start up script for slave device"""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

import gobject
import select
import Pyro4

from pisync.core import player
from pisync.core import poller

#TDOD: Possibly don't need this any-more, we'll see.
gobject.threads_init()
Pyro4.config.SERVERTYPE = "multiplex"

class Slave(object):
  def __init__(self,config):
    self.config = config
    self.slave_player = player.Player()
    #TODO: Seriously re-consider life as a programmer for using this workaround
    ip_address = Pyro4.socketutil.getIpAddress('localhost',True)
    self.pyro_daemon = Pyro4.Daemon(host=ip_address)
  
  def install_pyro_event_callback(self):
    """Add a callback to the gobject event loop to handle Pyro requests."""
    def pyro_event():
      while True:
        s,_,_ = select.select(self.pyro_daemon.sockets,[],[],0.01)
        if s:
          self.pyro_daemon.events(s)
        else:
          break
        gobject.timeout_add(20, pyro_event)
      return True
    gobject.timeout_add(20, pyro_event)
  
  def setup_pyro(self):
    """Sets up Pyro, sharing slave_player"""
    ns = Pyro4.locateNS()
    uri = self.pyro_daemon.register(self.slave_player)
    #TODO: Handle NS not found error
    ns.register("pisync.slave.%s" % self.config['device_id'],uri)

  def start(self):
    """Sets up Pyro, sharing slave_player, and starts the eventloop"""
    self.setup_pyro()
    self.install_pyro_event_callback()
    print 'Starting Main Loop'
    gobject.MainLoop().run()