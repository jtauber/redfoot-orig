# $Header$

from redfoot.rednode import RedNode
from redfoot.modules.editor import Editor
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


class UI:

    def __init__(self, location, uri):
        self.rednode = RedNode()
        import os
        if not os.access(location, os.F_OK):
            # create file
            self.rednode.local.save(location, uri)
        self.rednode.local.load(location, uri)
        self.editor = Editor(self.rednode)

    def handle_request(self, request, response):
        self.editor.handle_request(request, response)


if __name__ == '__main__':

    (port, location, uri) = get_args()

    server = RedServer(('', port))
    server.run("generic", location, uri)




