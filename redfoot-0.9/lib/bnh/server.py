# $Header$
"""
eikeon's Bare Naked HTTP Server
"""

__version__ = "$Revision$"


from bnh.receiver import Receiver
from bnh.servlet import ServerConnection
from bnh.servlet import ServerContext

from threading import RLock
from threading import Condition

class Server:
    def __init__(self, serverAddress):
        self.context = ServerContext()        
        self.receiver = Receiver(serverAddress)
        self.receiver.start()
        
    def setHandler(self, handler):
        self.handler = handler

    def start(self):
        sc = ServerConnection(self.handler, self.context)
        import threading
        t = threading.Thread(target = self._handleRequest, args = (sc,))
        t.setDaemon(1)
        t.start()

    def _handleRequest(self, serverConnection):
        handlerCubby = self.receiver.handlerCubby
        #while self.running==1:
        while 1:
            clientSocket = handlerCubby.get()
            if clientSocket!=None:
                serverConnection.handleRequest(self, clientSocket)
            else:
                handlerCubby.wait(0.05) # TODO: can we make this wait()?

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

