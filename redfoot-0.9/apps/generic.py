# $Header$

from redfoot.rednode import RedNode
from redfoot.modules.viewer import Viewer
from redfoot.server import RedServer
from rdf.query import QueryStore
from rdf.const import *

def get_args():

    import getopt
    import sys
    import string

    # set default values
    port = 8000
    location = "generic.rdf"
    uri = None

    optlist, args = getopt.getopt(sys.argv[1:], 'l:p:u:P:')
    for optpair in optlist:
        opt, value = optpair
        if opt=="-l":
            location = value
        elif opt=="-u":
            uri = value
        elif opt=="-p":
            port = string.atoi(value)

    # uri defaults to url when no uri is specified
    if uri==None:
        import socket
        hostname = socket.getfqdn('localhost')
        if port==80:
            uri = "http://%s/" % hostname
        else:
            uri = "http://%s:%s/" % (hostname,port)

    return (port, location, uri)


class UI(Viewer):

    def __init__(self, location, uri):
        self.rednode = RedNode()
        import os
        if not os.access(location, os.F_OK):
            # create file
            self.rednode.local.save(location, uri)
        self.rednode.local.load(location, uri)
        Viewer.__init__(self, self.rednode)
        self.showNeighbours = 1
        
    def handle_request(self, request, response):
        Viewer.handle_request(self, request, response)

#    def content(self, request, response):
#        path_info = request.get_path_info()
#        if hasattr(self, path_info):
#            apply(getattr(self, path_info), (request, response))
#            return

    def css(self):
        self.response.write("""
        body {
          margin:      10px;
        }

        form {
          margin:      0px;
          padding:     0px;
        }

        body, td, th {
          font-family: Verdana;
          font-size:   10pt;
        }

        div.box {
          border: solid 1pt #000;
          padding: 5px 10px;
        }

        h1 {
          font-family: Verdana;
          background:  #990000;
          font-weight: normal;
          color:       #FFF;
          padding:     5px 10px;
          margin:      -10px -10px 10px -10px;
        }

        p.MENUBAR {
          margin: -10px -10px 10px -10px;
          padding: 3px 20px;
          background:  #000000;
          color:       #CCCCCC;
        }

        p.MENUBAR a {
          color:       #CCCCCC;
          text-decoration: none;
        }

        p.MENUBAR a:visited {
          color:       #CCCCCC;
          text-decoration: none;
        }

        p.MENUBAR a:hover {
          color:       #FFFFFF;
          text-decoration: none;
        }

        h2 {
          font-family: Verdana;
          font-weight: normal;
          color:       #990000;
          margin:      0px;
        }

        h3 {
          font-family: Verdana;
          font-weight: normal;
        }

        a {
          color:       #000000;
        }

        a:visited {
          color:       #000000;
        }

        a:hover {
          color:       #990000;
        }

        dt {
          font-weight: bold;
        }

        table {
          border: solid 1pt #000;
          margin: 5px;
        }

        td {
          background: #CCC;
          margin: 0px;
          padding: 5px;
        }

        tr.REIFIED td {
          border: solid 1pt #990000;
	  background: #FFF;
        }

        p.WARNING {
          color: #C00;
        }

	textarea {
	  font-family: Verdana;
	}
        """)


if __name__ == '__main__':

    (port, location, uri) = get_args()

    server = RedServer(('', port))
    server.run("generic", location, uri)




