from redfoot.store import *
from redfoot.storeio import *
from redfoot.viewer import *
from redfoot.query import *

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

        tripleStore = TripleStore()

        storeIO = StoreIO()
        storeIO.setStore(tripleStore)
        storeIO.load("rdfSchema.rdf", "http://www.w3.org/2000/01/rdf-schema")
        storeIO.load("rdfSyntax.rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns")

        viewer = Viewer(self.wfile, QueryStore(tripleStore))
        viewer.mainPage()

        self.wfile.flush()
        self.wfile.close()

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

#    port = 8000
#    server_address = ('', port)

    import sys
    if sys.argv[1:]:
        port = string.atoi(sys.argv[1])
    else:
        port = 8000
    server_address = ('', port)

    httpd = ServerClass(server_address, HandlerClass)

    print "Serving HTTP on port", port, "...\n"
    httpd.serve_forever()


if __name__ == '__main__':
    runServer()
