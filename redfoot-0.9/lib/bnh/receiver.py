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
#~ Revision 6.1  2001/03/26 20:19:00  eikeon
#~ removed old header
#~
#~ Revision 6.0  2001/02/19 05:01:23  jtauber
#~ new release
