# $Header$

from redfoot.store import *
from redfoot.storeio import *
from redfoot.viewer import *
from redfoot.query import *
from redfoot.editor import *

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


class RedfootHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    """

    """

    server_version = "RedfootHTTP/" + __version__

    def do_GET(self):
        """Serve a GET request."""

        self.send_head()

        i = string.find(self.path, "?")
        if i==-1:
            path_info = self.path
            query_string = ""
        else:
            path_info = self.path[:i]
            query_string = self.path[i+1:]
            
        args = cgi.parse_qs(query_string)

        viewer = self.viewer
        viewer.setWriter(self.wfile)

        if args.has_key("processor"):
            if args["processor"][0] == "update":
                viewer.update(args)
            elif args["processor"][0] == "create":
                viewer.create(args)
            elif args["processor"][0] == "save":
                viewer.save()
            elif args["processor"][0] == "delete":
                viewer.delete(args)
            elif args["processor"][0][0:4] == "del_":
                viewer.deleteProperty(args)
            elif args["processor"][0][0:6] == "reify_":
                viewer.reifyProperty(args)
            elif args["processor"][0] == "connect":
                viewer.connect(args)
	                
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
            viewer.subclass(root, 0)
        elif path_info == "/classList":
            viewer.classList()
            
        elif path_info == "/RDF":
            viewer.RDF()
        elif path_info == "/Triples":
            viewer.Triples()
        elif path_info == "/css":
            viewer.css()
        elif path_info == "/view":
            viewer.view(args['uri'][0]) # TODO: check why values of args are lists
        elif path_info == "/edit":
            viewer.edit(args['uri'][0]) # TODO: check why values of args are lists
	elif path_info == "/add":
            if args.has_key("type"):
                type = args["type"][0]
            else:
                type = None
            viewer.add(type)
        elif path_info == "/connect":
            viewer.connectPage()
        else:
            # make a proper 404
            self.wfile.write("unknown PATH of '%s'" % path_info)

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
        self.send_header("Content-type", "text/html")
        self.send_header("Expires", "-1")
        self.end_headers()


def runServer():

    import sys
    if sys.argv[1:]:
        port = string.atoi(sys.argv[1])
    else:
        port = 8000
    server_address = ('', port)

    httpd = BaseHTTPServer.HTTPServer(server_address, RedfootHTTPRequestHandler)

    from redfoot.rednode import StoreNode
    storeNode = StoreNode()

    storeIO = StoreIO()
    storeIO.setStore(TripleStore())
    if sys.argv[3:]:
        storeIO.load(sys.argv[2], sys.argv[3])
    else:
        storeIO.load("tests/example.rdf", "http://redfoot.sourceforge.net/2000/09/24")

    storeNode.setStore(storeIO)

    UI = "PeerEditor"
    RedfootHTTPRequestHandler.viewer = eval("%s(None, storeNode)" % UI)

    print "Serving HTTP on port", port, "...\n"
    httpd.serve_forever()


if __name__ == '__main__':
    runServer()


# $Log$
# Revision 1.17  2000/10/08 06:27:41  jtauber
# switched over to using PeerEditor and added handling of connect page and connect processor
#
# Revision 1.16  2000/10/08 06:19:15  eikeon
# Changed default view to be the collapsed subclass view
#
# Revision 1.15  2000/10/08 06:05:03  eikeon
# UNKNOWN PATH now indicates the value of the unknown path
#
# Revision 1.14  2000/10/07 02:22:16  jtauber
# added handling of processor HTTP parameter for deletion and reification buttons
#
# Revision 1.13  2000/10/06 02:44:56  jtauber
# added save functionality but note it doesn't work yet
#
# Revision 1.12  2000/10/05 18:48:30  jtauber
# add now actually creates the resource entry
#
# Revision 1.11  2000/10/05 02:42:35  jtauber
# implemented UI for 'add' in editor
#
# Revision 1.10  2000/10/05 01:02:19  jtauber
# server now knows how to call update on editor
#
# Revision 1.9  2000/10/03 22:12:57  eikeon
# Fixed up ^
#
# Revision 1.8  2000/10/01 07:41:09  eikeon
# fixed missing imports etc from previous premature checkin ;(
#
# Revision 1.7  2000/10/01 07:31:47  eikeon
# StoreNode now does the loading of the rdf-syntax and rdf-schema; the runServer function now creates the Editor and gives it to the RedfootHTTPRequestHandler
#
# Revision 1.6  2000/10/01 03:58:10  eikeon
# fixed up all the places where I put CVS keywords as keywords in omments... duh
#
# Revision 1.5  2000/10/01 03:13:18  eikeon
# storeNode now contains a storeIO as its store; a StoreNode now gets passed in to the Editor's constructor... as Viewers (hence an Editor) now take storeNodes
#
# Revision 1.4  2000/10/01 02:25:09  eikeon
# modified to use the new StoreNode class; added Header and Log CVS keywords
