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
        self.viewer = None

    def getViewer(self):
        if self.viewer==None:
            from redfoot.rednode import StoreNode
            from redfoot.storeio import StoreIO
            from redfoot.store import TripleStore
            from redfoot.viewer import *
            from redfoot.editor import *
            
            storeNode = StoreNode()

            storeIO = StoreIO()
            storeIO.setStore(TripleStore())
            storeIO.load(location, uri)

            storeNode.setStore(storeIO)
            self.viewer = eval("%s(None, storeNode)" % interface)

        return self.viewer

    def handleRequest(self, request, response):
        args = request.parameters
        path_info = request.path_info

        self.lock.acquire()
        viewer = self.getViewer()
        viewer.setWriter(response)
        viewer.handler(path_info, args)
        self.lock.release()            


class RedfootServerConnection(ServerConnection):

    handler = RedfootHandler()

    def __init__(self):
        ServerConnection.__init__(self, None)
        self.handler = RedfootServerConnection.handler
        

if __name__ == '__main__':

    # set default values
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

    # uri defaults to url when no uri is specified
    if uri==None:
        import socket
        # method for calculating absolute hostname
        hostname = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0]
        uri = "http://%s:%s/" % (hostname,port)

    server = Server(('', port), lambda : RedfootServerConnection())
    
    import threading
    t = threading.Thread(target = server.start, args = ())
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
# Revision 2.3  2000/10/16 04:58:19  eikeon
# refactored plumb-ing between bnh.Server and RedfootHandler
#
# Revision 2.2  2000/10/16 01:56:10  eikeon
# removed 1.x log history
#
# Revision 2.1  2000/10/16 01:45:32  eikeon
# moved viewer request handling code from server to viewer
#
# Revision 2.0  2000/10/14 01:14:04  jtauber
# next version
