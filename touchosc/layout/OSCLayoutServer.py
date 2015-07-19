#!/usr/bin/env python
"""
Avahi-enabled TouchOSC layout server.
"""

import os
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import platform
import sys
import time
import zipfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

filename = 'amcp_template.touchosc'
PORT = 9658

def doit(filename):
    class OSCRequestHandler(SimpleHTTPRequestHandler):
        """OSCRequestHandler

        Hardcode the information necessary for TouchOSC to download the supplied
        layout file.

        """
        def send_head(self):
            """Hard coded single-file server.
            """
            self.send_response(200)
            self.send_header("Content-type", 'application/touchosc')
            self.send_header("Date", self.date_time_string(time.time()))
            self.send_header("Content-Disposition", 'attachment; filename="%s"' %
                (filename, ))
            self.end_headers()
            full_filename = os.path.join(os.path.dirname(__file__), filename)
            z = zipfile.ZipFile(full_filename)
            return z.open('index.xml', 'r')

    service = None
    if platform.system() == 'Linux':
        from avahi_announce import ZeroconfService
        service = ZeroconfService(
            name="Dreamland", port=PORT, stype="_touchosceditor._tcp")
        service.publish()
    server_address = ('', PORT)
    httpd = BaseHTTPServer.HTTPServer(server_address, OSCRequestHandler)
    try:
        httpd.serve_forever()
    finally:
        if service:
            service.unpublish()

if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) == 2 else 'dreamland_template.touchosc'
    doit(filename)
