__version__ = "$Revision$"

import socket, sys
from threading import Thread

class Receiver:
    ""

    def __init__(self, server_address, connection_queue):
        ""
        self.server_address = server_address
        self.connection_queue = connection_queue
        self.socket = None
        self.running = 0

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
        
    def _coverage_accept_requests(self, trace):
        if trace:
            sys.settrace(trace)
        self._accept_requests()
        
    def _accept_requests(self):        
        server_socket = self._get_socket()
        connection_queue = self.connection_queue
        while self.running:
            try:
                client_socket, client_address = server_socket.accept()
                connection_queue.put(client_socket)
            except socket.error:
                #TODO: log
                break
            except:
                import traceback
                traceback.print_exc()
                sys.stderr.flush()
                break
        
    def start(self):
        if not self.running:
            # TODO: check to see if already running.
            sys.stderr.write("Started Redfoot HTTP Server.\n")
            sys.stderr.flush()
            self.running = 1

            try:
                import coverage
                trace = sys._getframe().f_trace
                target = self._coverage_accept_requests
                args = (trace, )
                trace = sys._getframe().f_trace
            except ImportError:
                target = self._accept_requests
                args = ()
            t = Thread(target = target, name="Receiver", args = args)          
            self.thread = t
            t.setDaemon(1)
            t.start()

    def stop(self):
        if 1:
            return
        # TODO: ??
        self.running = 0
        if self.socket:
            self.socket.close()
            self.socket = None


