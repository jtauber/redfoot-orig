__version__ = "$Revision$"

from threading import Thread
from redfoot.server.error import BadRequestError

import socket

class Dispatcher:

    def __init__(self, connection_queue):
        self.connection_queue = connection_queue
        self.running = 0
        
    def set_handle_connection(self, handle_connection):
        self.handle_connection = handle_connection

    def start(self):
        try:
            import coverage
            import sys            
            trace = sys._getframe().f_trace
            target = self._debug_handle_connections            
            args = (self.handle_connection, trace)
        except ImportError:
            target = self._handle_connections
            args = (self.handle_connection,)            
            
        t = Thread(target = target,
                   name = "Dispatcher",
                   args = args)
        self.thread = t
        t.setDaemon(1)
        t.start()

    def stop(self):
        if self.running:
            self.running = 0
            self.connection_queue.put(None) # to for notify
            self.thread.join() # wait for pending request to finish
        
    def _debug_handle_connections(self, handle_connection, trace):
        if trace:
            import sys
            sys.settrace(trace)
        self._handle_connections(handle_connection)
        
    def _handle_connections(self, handle_connection):        
        self.running = 1            
        connection_queue = self.connection_queue
        while self.running==1 or not connection_queue.empty():
            client_socket = connection_queue.get()
            if client_socket!=None:
                try:
                    handle_connection(client_socket)                    
                except socket.error:
                    #TODO: log
                    pass
                except BadRequestError:
                    #TODO: log
                    pass
                except:
                    import traceback
                    traceback.print_exc()
                    import sys
                    sys.stdout.flush()
                    sys.stderr.flush()                    
                    
