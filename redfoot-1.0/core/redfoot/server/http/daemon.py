from redfoot.server.receiver import Receiver
from redfoot.server.dispatcher import Dispatcher
from Queue import Queue

from redfoot.server.daemon import Daemon
from redfoot.server.http.handler import HTTPConnectionHandler

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
    def __init__(self, serverAddress, name, handler_class):
        HTTPDaemon.__init__(self, serverAddress)
        daemons.append(self)
        self.name = name
        self.handler_class = handler_class
        self.server_address = serverAddress
        
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
            self.stop()

    def load(self, module, args=()):
        self.module = module
        self.args = args

        app_class = module.__redpages__
        instance = apply(app_class, args)
        servername, port = self.server_address
        if port==80:
            instance.URI = "http://%s/" % servername
        else:
            instance.URI = "http://%s:%s/" % (servername, port)
            
        handle_request = instance.handle_request
        instance.create_sub_modules()

        self.set_handle_request(handle_request)            
        self.start()

    def notify_me_of_reload(self, module):
        if module.__name__==self.module.__name__:
            self.stop()
            self.module = module            
            self.load(module, self.args)

            import sys
            sys.stderr.write("RELOADED '%s'\n" % module)
            sys.stderr.flush()


