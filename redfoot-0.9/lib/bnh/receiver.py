# $Header$

"""
eikeon's Bare Naked HTTP Server
"""

__version__ = "$Revision$"

import socket
import sys

class Receiver:
    ""

    def __init__(self, server_address, connection_cuby):
        ""
        self.server_address = server_address
        self.connection_cubby = connection_cuby

    def _get_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        sys.stderr.write("Attempting to bind to socket")
        while 1:
            try:
                sys.stderr.flush()
                self.socket.bind(self.server_address)
                break
            except:
                sys.stderr.write(".")
                sys.stderr.flush()
                import time
                time.sleep(1)
                continue
        sys.stderr.write("\nSuccessfully bound to socket\n")
        sys.stderr.flush()
        self.socket.listen(5)
        return self.socket
        

    def _accept_requests(self):
        server_socket = self._get_socket()
        connection_cubby = self.connection_cubby
        while 1:
            try:
                client_socket, client_address = server_socket.accept()
                connection_cubby.put(client_socket)
            except socket.error:
                #TODO: log
                break
            except:
                import traceback
                traceback.print_exc()
                sys.stderr.flush()
                break
        
    def start(self):
        sys.stderr.write("Started eikeon's Bare Naked HTTP Server.\n")
        sys.stderr.flush()
        self.running = 1
        import threading
        t = threading.Thread(target = self._accept_requests, args = ())
        self.thread = t
        t.setDaemon(1)
        t.start()

    def stop(self):
        self.socket.close()
        del self.socket

    

#~ $Log$
#~ Revision 5.7  2000/12/20 21:22:07  eikeon
#~ converted many mixedCase names to _ style names
#~
#~ Revision 5.6  2000/12/17 22:33:10  eikeon
#~ changing names to _ style names; moved ConnectionCubby to its own module
#~
#~ Revision 5.5  2000/12/17 21:19:10  eikeon
#~ removed old log messages
#~
#~ Revision 5.4  2000/12/14 00:39:32  eikeon
#~ moved attempting to bind to socket message out of loop
#~
#~ Revision 5.3  2000/12/14 00:32:38  eikeon
#~ added code to keep trying to bind to address
#~
#~ Revision 5.2  2000/12/13 00:03:37  eikeon
#~ server now shuts down cleanly
#~
#~ Revision 5.1  2000/12/12 22:20:50  eikeon
#~ added shutdown code... to shutdown cleanly
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
