from redfoot.store import *
from redfoot.storeio import *

"""redfoot HTTP Server.

This module builds on BaseHTTPServer...

"""


__version__ = "0.0"


import os
import string
import posixpath
import BaseHTTPServer
import urllib
import cgi
from StringIO import StringIO


class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """

    """

    server_version = "RedfootHTTP/" + __version__

    def do_GET(self):
        """Serve a GET request."""

        self.wfile.write("<ul>")

        tripleStore = TripleStore()

        storeIO = StoreIO()
        storeIO.setStore(tripleStore)
        storeIO.load("rdfSchema.rdf")

        class Visitor:
            def __init__(self, wfile):
                self.wfile = wfile
                
            def callback(self, subject, property, value):
                self.wfile.write("<li>s:%s</li><li>-p:%s</li><li>--v:%s</li>" % (subject, property, value))

        visitor = Visitor(self.wfile)
        tripleStore.visit(visitor, None, None, None)

        self.wfile.write("</ul>")

    def do_HEAD(self):
        """Serve a HEAD request."""

        self.send_head()


    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.
        """

        self.send_response(200)
        self.send_header("Content-type", "text/HTML")
        self.send_header("Expires", "-1")
        self.end_headers()




def runServer(HandlerClass = SimpleHTTPRequestHandler,
         ServerClass = BaseHTTPServer.HTTPServer):

    port = 80
    server_address = ('', port)

    httpd = ServerClass(server_address, HandlerClass)

    print "Serving HTTP on port", port, "...\n"
    httpd.serve_forever()


if __name__ == '__main__':
    runServer()
