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
        # TODO: check to see if already running.
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
#~ Revision 8.0  2001/04/27 00:52:13  eikeon
#~ new release
