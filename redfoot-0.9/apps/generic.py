# $Header$

from redfoot.rednode import RedNode
from redfoot.baseUI import BaseUI
from redfoot.editor import PeerEditor
from redfoot.server import RedServer
from rdf.query import QueryStore
from rdf.const import *

if __name__ == '__main__':

    (port, location, uri) = get_args()

    server = RedServer(('', port))
    server.run("generic", location, uri)


def get_args():

    import getopt
    import sys
    import string

    # set default values
    port = 8000
    location = "local.rdf"
    uri = None
    path = ""

    optlist, args = getopt.getopt(sys.argv[1:], 'l:p:u:P:')
    for optpair in optlist:
        opt, value = optpair
        if opt=="-l":
            location = value
        elif opt=="-u":
            uri = value
        elif opt=="-p":
            port = string.atoi(value)
        elif opt=="-P":
            if value[-1:]=='/':
                value = value[0:-1]
            path = value

    # uri defaults to url when no uri is specified
    if uri==None:
        import socket
        hostname = socket.getfqdn('localhost')
        uri = "http://%s:%s%s" % (hostname,port,path)

    return (port, location, uri)


class UI:

    def __init__(self, location, uri):
        self.storeNode = RedNode()
        self.storeNode.local.load(location, uri)
        self.editor = PeerEditor(self.storeNode)

    def handle_request(self, request, response):
        self.editor.handle_request(request, response)



