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

        self.send_head()

        tripleStore = TripleStore()

        storeIO = StoreIO()
        storeIO.setStore(tripleStore)
        storeIO.load("rdfSchema.rdf", "http://www.w3.org/2000/01/rdf-schema")
        storeIO.load("rdfSyntax.rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns")
        storeIO.load("example.rdf", "http://redfoot.sourceforge.net/2000/09/24")
        
        i = string.find(self.path, "?")
        if i==-1:
            path_info = self.path
            query_string = ""
        else:
            path_info = self.path[:i]
            query_string = self.path[i+1:]
            
        args = cgi.parse_qs(query_string)

        viewer = Viewer(self.wfile, QueryStore(tripleStore))

        if path_info == "/":
            viewer.mainPage()
        elif path_info == "/subclass":
            if args.has_key("uri"):
                root = args["uri"][0] # TODO: check why values of args are lists
            else:
                root = QueryStore.RESOURCE
            viewer.subclass(root)
        elif path_info == "/subclassNR":
            if args.has_key("uri"):
                root = args["uri"][0] # TODO: check why values of args are lists
            else:
                root = QueryStore.RESOURCE
            viewer.subclassNonRecursive(root)
        elif path_info == "/RDF":
            viewer.RDF()
        elif path_info == "/Triples":
            viewer.Triples()
        elif path_info == "/css":
            viewer.css()
        elif path_info == "/view":
            viewer.view(args['uri'][0]) # TODO: check why values of args are lists
        else:
            # make a proper 404
            self.wfile.write("unknown PATH")

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
