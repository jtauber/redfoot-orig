from redfoot.server.receiver import Receiver
from redfoot.server.dispatcher import Dispatcher
from Queue import Queue

class Daemon:
    def __init__(self, serverAddress):
        connection_queue = Queue(5)        
        self.receiver = Receiver(serverAddress, connection_queue)
        self.dispatcher = Dispatcher(connection_queue)

    def set_handle_connection(self, handler):
        self.dispatcher.set_handle_connection(handler)

    def start(self):
        self.receiver.start()
        self.dispatcher.start()

    def stop(self):
        self.receiver.stop()
        self.dispatcher.stop()
