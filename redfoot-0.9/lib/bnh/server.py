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
#~ Revision 5.6  2000/12/17 23:35:53  eikeon
#~ split off ServerConnection and company into their own module
#~
#~ Revision 5.5  2000/12/17 22:33:10  eikeon
#~ changing names to _ style names; moved ConnectionCubby to its own module
#~
#~ Revision 5.4  2000/12/17 21:19:10  eikeon
#~ removed old log messages
#~
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
