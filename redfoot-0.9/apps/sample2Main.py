def encodeURI(s, safe='/'):
    import string
    always_safe = string.letters + string.digits + ' _,.-'
    safe = always_safe + safe
    res = []
    for c in s:
        if c not in safe:
            res.append('%%%02x'%ord(c))
        else:
            if c==' ':
                res.append('+')
            else:
                res.append(c)
    return string.joinfields(res, '')


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
        
LASTRETRIEVED = "http://redfoot.sourceforge.net/2001/01/30/#lastRetrieved"

SELF = "http://localhost:8001/"
FRIEND = "http://localhost:8002/"

def _pull(interval):
    while 1:
        import time
        time.sleep(interval)

        sys.stderr.write("pulling")
        sys.stderr.flush()
        from urllib2 import urlopen, Request
        headers = {}
        headers['Accept-Language'] = 'rdf'

        last = storeNode.getFirst(FRIEND, LASTRETRIEVED, None)
        url = FRIEND
        if last!=None:
            url = url + "?since=%s" % encodeURI(last[2])
        request = Request(url, None, headers)

        # For now just put the current time...
        # Later we should put the time of the last timestamp we get back from the query
        timestamp = storeNode.local.generateURI()
        bookkeeping.remove(FRIEND, LASTRETRIEVED, None)
        bookkeeping.add(FRIEND, LASTRETRIEVED, timestamp)        

        try:
            f = urlopen(request)
            storeNode.local.update_journal(f, FRIEND)

            f.close()
        except:
            sys.stderr.write(".")
            sys.stderr.flush()
        




from redfoot.rednode import RedNode
storeNode = RedNode()
storeNode.local = JournalingStoreLocal()
storeNode.local.load("sample2.rdf", SELF)
bookkeeping = Local()
bookkeeping.load("bookkeeping.rdf", SELF)
storeNode.neighbours.addNeighbour(bookkeeping)

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



