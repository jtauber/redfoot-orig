# $Header$
"""
eikeon's Bare Naked HTTP Server
"""

__version__ = "$Revision$"

from bnh.receiver import Receiver
from bnh.connection_cubby import ConnectionCubby
from bnh.server_context import ServerContext

from bnh.servlet import ServerConnection

class Server:
    def __init__(self, serverAddress):
        self.context = ServerContext()
        self.connection_cubby = ConnectionCubby(5)

        # Listen for requests and queue up the connections in the ConnectionCubby
        receiver = Receiver(serverAddress, self.connection_cubby)
        receiver.start()
        
    def set_handler(self, handler):
        self.handler = handler

    def start(self):
        server_connection = ServerConnection(self.handler, self.context)
        import threading
        t = threading.Thread(target = self._handle_request, args = (server_connection,))
        self.thread = t
        t.setDaemon(1)
        t.start()

    def stop(self):
        self.running = 0
        self.connection_cubby.notify()
        self.thread.join() # wait for pending request to finish

    def _handle_request(self, server_connection):
        self.running = 1            
        connection_cubby = self.connection_cubby
        while self.running==1 or not connection_cubby.empty():
            client_socket = connection_cubby.get()
            if client_socket!=None:
                server_connection.handle_request(self, client_socket)
            else:
                connection_cubby.wait() 

#~ $Log$
#~ Revision 6.1  2001/03/26 20:19:01  eikeon
#~ removed old header
#~
#~ Revision 6.0  2001/02/19 05:01:23  jtauber
#~ new release
