# $Header$
"""
eikeon's Bare Naked HTTP Server
"""

__version__ = "$Revision$"

from bnh.receiver import Receiver
from bnh.servlet import ServerConnection
from bnh.servlet import ServerContext

class Server:
    def __init__(self, serverAddress):
        self.context = ServerContext()        
        self.receiver = Receiver(serverAddress)
        self.receiver.start()
        self.running = 0
        
    def setHandler(self, handler):
        self.handler = handler

    def start(self):
        serverConnection = ServerConnection(self.handler, self.context)
        import threading
        t = threading.Thread(target = self._handleRequest, args = (serverConnection,))
        t.setDaemon(1)
        t.start()

    def stop(self):
        self.running = 0

    def _handleRequest(self, serverConnection):
        self.running = 1            
        handlerCubby = self.receiver.handlerCubby
        while self.running==1:
            clientSocket = handlerCubby.get()
            if clientSocket!=None:
                serverConnection.handleRequest(self, clientSocket)
            else:
                handlerCubby.wait(0.05) # TODO: can we make this wait()?

#~ $Log$
#~ Revision 5.2  2000/12/13 00:03:37  eikeon
#~ server now shuts down cleanly
#~
#~ Revision 5.1  2000/12/12 22:20:50  eikeon
#~ added shutdown code... to shutdown cleanly
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
#~
#~ Revision 4.7  2000/12/07 20:19:07  eikeon
#~ fixing up autoreload after server refactors
#~
#~ Revision 4.6  2000/12/04 15:00:30  eikeon
#~ cleaned up imports
#~
#~ Revision 4.5  2000/12/04 05:21:24  eikeon
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
#~

