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
#~ Revision 5.3  2000/12/14 00:53:19  eikeon
#~ removed self.receiver.stop()... only want to stop server handler
#~
#~ Revision 5.2  2000/12/13 00:03:37  eikeon
#~ server now shuts down cleanly
#~
#~ Revision 5.1  2000/12/12 22:20:50  eikeon
#~ added shutdown code... to shutdown cleanly
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
