import threading
import getopt
import sys
from sample2 import Sample2
from redfoot.rednode import *


def _start_thread(notMoreOftenThan=15):
    """Not more often then is in seconds"""
    import threading
    t = threading.Thread(target = _pull, args = (notMoreOftenThan,))
    t.setDaemon(1)
    t.start()
        
def _pull(interval):
    while 1:
        import time
        time.sleep(interval)

        sys.stderr.write("pulling")
        sys.stderr.flush()
        from urllib2 import urlopen, Request
        headers = {}
        headers['Accept-Language'] = 'rdf'
        request = Request("http://localhost:8002/", None, headers)
        f = urlopen(request)
        storeNode.local.update_journal(f, "http://localhost:8002/")
        f.close()
        




from redfoot.rednode import RedNode
storeNode = RedNode()
storeNode.local = JournalingStoreLocal()
storeNode.local.load("sample2.rdf", "http://localhost:8001/")

_start_thread()

port = 8001
optlist, args = getopt.getopt(sys.argv[1:], 'p:')
for optpair in optlist:
    opt, value = optpair
    if opt=="-p":
        import string
        port = string.atoi(value)

from redfoot.server import RedServer
redserver = RedServer(('', port))
    
redserver.set_handler(Sample2(storeNode))
redserver.start()
while 1:
    try:
        threading.Event().wait(100)
    except KeyboardInterrupt:
        break
sys.stderr.write("Shutting down xteam\n")
sys.stderr.flush()



