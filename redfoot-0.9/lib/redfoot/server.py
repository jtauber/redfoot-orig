# $Header$

"""
Redfoot specific server code.
"""

__version__ = "$Revision$"

from bnh.server import Server
import sys
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
            viewer.handleRequest(request, response)
        finally:
            self.lock.release()            


class RedServer:
    def runServer(self, args):
        # set default values
        port = 8000
        location = "local.rdf"
        uri = None

        path = ""
        

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
            #hostname = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0]
            hostname = socket.getfqdn('localhost')
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

    
        server = Server(('', port))
        server.start()

        self.server = server
        self.path = path
        self.storeNode = storeNode
        
        sys.stderr.write("REDFOOT: serving %s (%s) on port %s...\n" % (location, uri, port))
        sys.stderr.write("... try hitting %s/classList for an editor\n" % uri)    
        sys.stderr.flush()
        

    def keepRunning(self):
        while 1:
            try:
                import threading
                threading.Event().wait(100)
            except KeyboardInterrupt:
                sys.exit()

if __name__ == '__main__':
    import sys
    redserver = RedServer()
    redserver.runServer(sys.argv[1:])
    from redfoot.editor import PeerEditor

    handler = PeerEditor(redserver.storeNode, redserver.path)
    redserver.server.addHandler(handler)
    
    redserver.keepRunning()

#~ $Log$
#~ Revision 4.0  2000/11/06 15:57:34  eikeon
#~ VERSION 4.0
#~
#~ Revision 3.4  2000/11/04 01:26:59  eikeon
#~ changed to python 2.0 method of getting the fully qualified domain name... as the 1.6 method in some instances would take a long time
#~
#~ Revision 3.3  2000/11/03 23:04:08  eikeon
#~ Added support for cookies and sessions; prefixed a number of methods and variables with _ to indicate they are private; changed a number of methods to mixed case for consistency; added a setHeader method on response -- headers where hardcoded before; replaced writer with response as writer predates and is redundant with repsonse; Added authentication to editor
#~
#~ Revision 3.2  2000/11/02 21:48:27  eikeon
#~ removed old log messages
#~
# Revision 3.1  2000/10/31 05:03:08  eikeon
# mainly Refactored how parameters are accessed (no more [0]'s); some cookie code; a few minor changes regaurding plumbing
#
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
