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

    def handleRequest(self, request, response):
        self.lock.acquire()
        try:
            viewer = self.viewer
            viewer.setWriter(response)
            viewer.handleRequest(request, response)
        finally:
            self.lock.release()            


def runServer(args, interface):
    # set default values
    port = 8000
    location = "local.rdf"
    uri = None

    path = ""
        
    import sys
    import getopt
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
        # method for calculating absolute hostname
        hostname = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0]
        uri = "http://%s:%s%s" % (hostname,port,path)

    from redfoot.rednode import StoreNode
    from rdf.storeio import StoreIO
    from rdf.store import TripleStore
            
    storeNode = StoreNode()

    # TODO: do this lazily on storeNode.load method?
    storeIO = StoreIO()
    storeIO.setStore(TripleStore()) # TODO: do this lazily
    storeIO.load(location, uri)
    storeNode.setStore(storeIO)

    redfootHandler = RedfootHandler()    
    redfootHandler.viewer = interface(None, storeNode, path)
    
    server = Server(('', port))
    server.addHandler(redfootHandler)
    server.start()

    sys.stderr.write("REDFOOT: serving %s (%s) with %s on port %s...\n" % (location, uri, interface, port))
    sys.stderr.write("... try hitting %s/classList for an editor\n" % uri)    
    sys.stderr.flush()
        

    while 1:
        try:
            import threading
            threading.Event().wait(100)
        except KeyboardInterrupt:
            sys.exit()

if __name__ == '__main__':
    import sys
    from redfoot.editor import PeerEditor
    runServer(sys.argv[1:], PeerEditor)


#~ $Log$
# Revision 3.1  2000/10/31 05:03:08  eikeon
# mainly Refactored how parameters are accessed (no more [0]'s); some cookie code; a few minor changes regaurding plumbing
#
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
