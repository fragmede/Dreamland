#!/usr/bin/env python
"""
TouchOSC translator

This advertises itself as a TouchOSC Host, takes button input, and sends
Zero-MQ messages.

"""

import logging
import platform
import sys

import liblo

sys.path.append("../")

import pubSubDreamland as psdl

logger = logging.getLogger('dreamland')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

BROADCAST_IP = '10.10.10.255'
send_port = '5560'

send_value_table = {0: 'low', 1: 'high'}

class Reciever():
    def __init__(self):
        self.pub = psdl.Publisher(None, send_port, 'touchosc')

    def send(self, section, number, raw_value):
        send_value = send_value_table[raw_value]
        msg = '%s %s' % (number, send_value)
        self.pub.sendMessage(section, msg)
        logger.info("Sent %s to %s.", msg, section)

fire_map = {
    'fire_main': 0,
    'fire_sm_1': 1,
    'fire_sm_2': 2,
    'fire_sm_3': 3,
    }
which_map = {'carousel':fire_map}

class TouchOSCServer(liblo.Server):

    def __init__(self, port, client_ip, client_port):
        liblo.Server.__init__(self, port)
        self.client = liblo.Address(client_ip, client_port)

        logger.info('action="init_server", port="%s", client_port="%s"',
                     port, client_port)

        self.reciever = Reciever()

    @liblo.make_method(None, None)
    def catch_all(self, path, args):
        logger.info("Recieved %s - %s", path, args)
        p = path.split("/")
        system = p[1]
        which = which_map[system][p[2]]
        value = int(args[0])
        self.reciever.send(system, which, value)

    def mainLoop(self):
        while True:
            # Drain all pending messages without blocking
            while self.recv(0):
                pass

if __name__ == "__main__":

    try:
        server = TouchOSCServer(port=8000, client_ip=BROADCAST_IP, client_port=9000)
    except liblo.ServerError, err:
        print str(err)
        sys.exit()

    if platform.system() == "Darwin":
        service = None
    else:
        # Avahi announce so it's findable on the controller by name
        from avahi_announce import ZeroconfService
        service = ZeroconfService(
            name="Dreamland TouchOSC Server", port=8000, stype="_osc._udp")
        service.publish()

    # Main thread runs both our LED effects and our OSC server,
    # draining all queued OSC events between frames. Runs until killed.

    try:
        server.mainLoop()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('action="server_shutdown"')
        # Cleanup
        if service:
            service.unpublish()
