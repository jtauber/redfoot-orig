# $Header$

"""
eikeon's Bare Naked HTTP Server
"""

__version__ = "$Revision$"

import socket
import sys

from servlet import *

class Receiver:
    ""

    def __init__(self, server_address):
        ""
        self.server_address = server_address
        self.handlerCubby = HandlerCubby(5)
        self.context = ServerContext()        

    def _acceptRequests(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        self.socket.bind(self.server_address)
        self.socket.listen(5)
        while 1:
            try:
                clientSocket, client_address = self.socket.accept()
                self.handlerCubby.put(clientSocket)
            except socket.error:
                #TODO: log
                break

    def start(self):
        sys.stderr.write("Started eikeon's Bare Naked HTTP Server.\n")
        sys.stderr.flush()
        import threading
        t = threading.Thread(target = self._acceptRequests, args = ())
        t.setDaemon(1)
        t.start()



from threading import RLock
from threading import Condition

class HandlerCubby:

    def __init__(self, limit):
        self.mon = RLock()
        self.rc = Condition(self.mon)
        self.wc = Condition(self.mon)
        self.limit = limit
        self.queue = []

    def put(self, item):
        self.mon.acquire()
        while len(self.queue) >= self.limit:
            self.wc.wait()
        self.queue.append(item)
        self.rc.notify()
        self.mon.release()

    def get(self):
        self.mon.acquire()
        if not self.queue:
            item = None
        else:
            item = self.queue[0]
            del self.queue[0]
            self.wc.notify()
        self.mon.release()
        return item

    def wait(self, timeout=None):
        self.mon.acquire()
        self.rc.wait(timeout)
        self.mon.release()

    def stop(self, handler):
        self.mon.acquire()
        handler.running = 0
        self.rc.notifyAll()
        self.mon.release()
    

#~ $Log$
#~ Revision 4.4  2000/12/04 02:02:56  eikeon
#~ removed debug output
#~
#~ Revision 4.3  2000/12/01 01:27:31  eikeon
#~ added session reaper code
#~
#~ Revision 4.2  2000/11/28 15:35:04  eikeon
#~ Move creation of ServerContext to Server
#~
#~ Revision 4.1  2000/11/09 21:14:21  eikeon
#~ made cookies persist for 24 hours
#~
#~ Revision 4.0  2000/11/06 15:57:33  eikeon
#~ VERSION 4.0
#~
#~ Revision 3.6  2000/11/06 01:11:29  eikeon
#~ added ability to stop a 'handler'; introduced a HandlerCubby to manage state between the server and handlers
#~
#~ Revision 3.5  2000/11/03 23:04:08  eikeon
#~ Added support for cookies and sessions; prefixed a number of methods and variables with _ to indicate they are private; changed a number of methods to mixed case for consistency; added a setHeader method on response -- headers where hardcoded before; replaced writer with response as writer predates and is redundant with repsonse; Added authentication to editor
#~
#~ Revision 3.4  2000/11/03 19:52:00  eikeon
#~ first pass at sessions... needs cleanup
#~
#~ Revision 3.3  2000/11/02 21:48:26  eikeon
#~ removed old log messages
#~
# Revision 3.2  2000/10/31 05:03:07  eikeon
# mainly Refactored how parameters are accessed (no more [0]'s); some cookie code; a few minor changes regaurding plumbing
#
# Revision 3.1  2000/10/27 16:20:02  eikeon
# small cleanup... mostly formatting
#
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
