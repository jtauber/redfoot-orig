# $Header$

"""
eikeon's Bare Naked HTTP Server
"""

__version__ = "$Revision$"

import socket
import sys

class Receiver:
    ""

    def __init__(self, server_address):
        ""
        self.server_address = server_address
        self.handlerCubby = HandlerCubby(5)

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
#~ Revision 4.1  2000/12/04 05:21:24  eikeon
#~ Split server.py into server.py, servlet.py and receiver.py
#~
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