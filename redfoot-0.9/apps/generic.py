# $Header$

from rdf.query import QueryStore
from redfoot.rednode import RedNode
from redfoot.baseUI import BaseUI
from redfoot.editor import PeerEditor

from rdf.const import *

import sys

if __name__ == '__main__':
    from redfoot.server import RedServer

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

    from redfoot.rednode import RedNode

    storeNode = RedNode()
    storeNode.local.load(location, uri)

    server = RedServer(('', port))
    server.setHandler(PeerEditor(storeNode, path))
    server.start()

    sys.stderr.write("REDFOOT: serving %s (%s) on port %s...\n" % (location, uri, port))
    sys.stderr.write("... try hitting %s/classList for an editor\n" % uri)    
    sys.stderr.flush()

    server.keepRunning()
            


