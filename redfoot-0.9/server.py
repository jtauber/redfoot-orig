# $Header$

"""
Redfoot specific server code.
"""

__version__ = "$Revision$"

from bnh.server import Server, ServerConnection
import string

class RedfootHandler:

    def __init__(self):
        import threading
        self.lock = threading.Lock()

    def handleRequest(self, request, response):
        args = request.parameters
        path_info = request.path_info

        self.lock.acquire()
        self.viewer.setWriter(response)
        self.viewer.handler(path_info, args)
        self.lock.release()            


class ServerConnectionFactory:

    def __init__(self, handler):
        self.handler = handler

    def createServerConnection(self):
        return ServerConnection(self.handler)
    

from redfoot.store import *
from redfoot.storeio import *
from redfoot.viewer import *
from redfoot.query import *
from redfoot.editor import *

if __name__ == '__main__':

    port = 8000
    location = "local.rdf"
    uri = None
    interface = "PeerEditor"
    
    import sys

    import getopt
    optlist, args = getopt.getopt(sys.argv[1:], 'i:l:p:u:')
    for optpair in optlist:
        opt, value = optpair
        if opt=="-l":
            location = value
        elif opt=="-u":
            uri = value
        elif opt=="-p":
            port = string.atoi(value)
        elif opt=="-i":
            interface = value

    if uri==None:
        import socket
        hostname = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0]
        uri = "http://%s:%s/" % (hostname,port)

    server_address = ('', port)

    from redfoot.rednode import StoreNode
    storeNode = StoreNode()

    storeIO = StoreIO()
    storeIO.setStore(TripleStore())
    storeIO.load(location, uri)

    storeNode.setStore(storeIO)

    redfootHandler = RedfootHandler()
    redfootHandler.viewer = eval("%s(None, storeNode)" % interface)

    serverConnectionFactory =  ServerConnectionFactory(redfootHandler)
    
    server = Server(server_address, serverConnectionFactory.createServerConnection)
    
    import threading
    t = threading.Thread(target = server.start,
                         args = ())
    t.setDaemon(1)
    t.start()

    sys.stderr.write("REDFOOT: serving %s (%s) with %s on port %s...\n" % (location, uri, interface, port))
    sys.stderr.flush()
        

    while 1:
        try:
            threading.Event().wait(100)
        except KeyboardInterrupt:
            sys.exit()


# $Log$
# Revision 2.1  2000/10/16 01:45:32  eikeon
# moved viewer request handling code from server to viewer
#
# Revision 2.0  2000/10/14 01:14:04  jtauber
# next version
