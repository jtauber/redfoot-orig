# $Header$
#
#  Copyright (c) 2000, James Tauber and Daniel Krech
#
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the
#     distribution.
#
#   * Neither name of James Tauber nor Daniel Krech may be used to
#     endorse or promote products derived from this software without
#     specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
#  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
#  OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
#  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
#  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
#  DAMAGE.
#
"""
eikeon's Bare Naked HTTP Server
"""

__version__ = "$Revision$"

from bnh.receiver import Receiver
from bnh.connection_cubby import ConnectionCubby

from bnh.servlet import ServerConnection

class Server:
    def __init__(self, serverAddress):
        self.connection_cubby = ConnectionCubby(5)

        # Listen for requests and queue up the connections in the
        # ConnectionCubby
        receiver = Receiver(serverAddress, self.connection_cubby)
        receiver.start()
        
    def set_handler(self, handler):
        self.handler = handler

    def start(self):
        server_connection = ServerConnection(self.handler)
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
#~ Revision 8.0  2001/04/27 00:52:13  eikeon
#~ new release
