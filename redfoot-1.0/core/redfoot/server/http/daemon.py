from redfoot.server.receiver import Receiver
from redfoot.server.dispatcher import Dispatcher
from Queue import Queue

from redfoot.server.daemon import Daemon
from redfoot.server.http.handler import HTTPConnectionHandler

from redfoot.version import VERSION

class HTTPDaemon(Daemon):
    def __init__(self, serverAddress):
        Daemon.__init__(self, serverAddress)

    def set_handle_request(self, handle_request):
        connection_handler = HTTPConnectionHandler(handle_request)
        self.set_handle_connection(connection_handler.handle_connection)

    def start(self):
        self.receiver.start()
        self.dispatcher.start()

    def stop(self):
        self.receiver.stop()
        self.dispatcher.stop()


daemons = []
def notify_me_of_reload(module):
    for redDaemon in daemons:
        redDaemon.notify_me_of_reload(module)
    

class RedDaemon(HTTPDaemon):
    def __init__(self, serverAddress, name, handler_class, exact=0):
        if exact:
            address = serverAddress
        else:
            address = ('', serverAddress[1])
        HTTPDaemon.__init__(self, address)
        daemons.append(self)
        self.name = name
        self.handler_class = handler_class
        self.server_address = serverAddress
        print "Redfoot", VERSION
        
    def run(self):
        from redfoot.lang.redcode.importer import RedcodeModuleImporter
        importer = RedcodeModuleImporter(self.handler_class)
        importer.install()

        module = __import__(self.name, globals(), locals(), ['*'])
        self.load(module)            
        
        try:
            while 1:        
                import threading
                threading.Event().wait(100)
        except KeyboardInterrupt:
            print "Shutting down..."
            self.stop()

    def load(self, module):
        self.module = module

        instance = module._RF_get_app()
        module._app_instance = instance

        servername, port = self.server_address
        if port==80:
            instance.URI = "http://%s/" % servername
        else:
            instance.URI = "http://%s:%s/" % (servername, port)
            
        handle_request = instance.handle_request
        self.set_handle_request(handle_request)            
        self.start()
        if port==80:
            print "Running at http://%s/" % servername
        else:
            print "Running at http://%s:%s/" % (servername, port)

    def stop(self):
        self.module._app_instance.stop()
        HTTPDaemon.stop(self)

    def notify_me_of_reload(self, module):
        if module.__name__==self.module.__name__:
            self.stop()
            self.module = module            
            self.load(module)

            import sys
            sys.stderr.write("RELOADED '%s'\n" % module)
            sys.stderr.flush()


