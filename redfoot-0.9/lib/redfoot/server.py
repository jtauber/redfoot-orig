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
        args = request.parameters
        path_info = request.path_info

        self.lock.acquire()
        try:
            viewer = self.viewer
            viewer.setWriter(response)
            viewer.handler(path_info, args)
        finally:
            self.lock.release()            


def runServer(args, interface):
    # set default values
    port = 8000
    location = "local.rdf"
    uri = None

    path = "/"
        
    import sys
    import getopt
    optlist, args = getopt.getopt(sys.argv[1:], 'i:l:p:u:P:')
    for optpair in optlist:
        opt, value = optpair
        if opt=="-l":
            location = value
        elif opt=="-u":
            uri = value
        elif opt=="-p":
            port = string.atoi(value)
        elif opt=="-P":
            path = value
            
    # uri defaults to url when no uri is specified
    if uri==None:
        import socket
        # method for calculating absolute hostname
        hostname = socket.gethostbyaddr(socket.gethostbyname(socket.gethostname()))[0]
        uri = "http://%s:%s%s" % (hostname,port,path)

    from redfoot.rednode import StoreNode
    from redfoot.storeio import StoreIO
    from redfoot.store import TripleStore
            
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
    sys.stderr.flush()
        

    while 1:
        try:
            import threading
            threading.Event().wait(100)
        except KeyboardInterrupt:
            sys.exit()

if __name__ == '__main__':
    import sys
    runServer(sys.argv[1:])


# $Log$
# Revision 1.1  2000/10/25 20:40:31  eikeon
# changes relating to new directory structure
#
# Revision 2.7  2000/10/17 02:29:43  jtauber
# set up server to be able to use SampleUI; fixed slash problem with path
#
# Revision 2.6  2000/10/17 01:50:43  jtauber
# server now takes -P option to pass in path which gets passed to the viewer
#
# Revision 2.5  2000/10/17 00:12:47  eikeon
# fixed bug causing server to hang under load
#
# Revision 2.4  2000/10/16 06:31:49  eikeon
# fixed bug I just introduced where a new RedfootHandler is beging created for each request
#
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
