"""poller.py: Handles polling the cloud server."""

__author__ = "Tom Hanson"
__copyright__ = "Copyright 2014"
__credits__ = ["Tom Hanson"]

__license__ = "GPL"
__maintainer__ = "Tom Hanson"
__email__ = "tom@aporcupine.com"

import urllib2
import config
import json

from Pyro4 import Proxy


#TODO: Decide whether or not to make this into a class
def poll_for_updates(master_config, master_player):
  """Polls the server and calls appropriate action with response"""
  print 'Polling...'
  response = make_request(master_config['group_id'])
  if 'actions' in response:
    for action in response['actions']:
      print 'Handling Action'
      handle_action(action, master_player, master_config['device_id'])
  
def make_request(group_id):
  json_string = json.dumps({'group_id': group_id})
  url = '%s/api/group/update' % config.BASE_URL
  req = urllib2.Request(url, json_string, {'Content-Type': 'application/json'})
  #TODO: Add error handling for HTTP errors
  f = urllib2.urlopen(req)
  response = json.loads(f.read())
  f.close()
  return response

def handle_action(action, master_player, master_device_id):
  if action['device_id'] == master_device_id:
    player = master_player
  else:
    player = Proxy('PYRONAME:pisync.slave.%s' % action['device_id'])
  # TODO: Handle security here, this is not too safe right now
  if action['type'] in ['play_list','set_volume']:
    getattr(player, action['type'])(action['arg'])
  elif hasattr(player, action['type']):
      getattr(player, action['type'])()
  else:
    print 'Invalid action provided'
      
    
  