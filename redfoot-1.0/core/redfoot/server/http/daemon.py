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
    def __init__(self, serverAddress, name, handlers, exact=0):
        if exact:
            address = serverAddress
        else:
            address = ('', serverAddress[1])
        HTTPDaemon.__init__(self, address)
        daemons.append(self)
        self.name = name
        self.handlers = handlers
        self.server_address = serverAddress
        print "Redfoot", VERSION
        
    def run(self):
        from redfoot.lang.redcode.importer import RedcodeModuleImporter
        importer = RedcodeModuleImporter(self.handlers)
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

        servername, port = self.server_address

        instance = module._RF_get_app(self.uri)
        module._app_instance = instance

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


class RDFRedDaemon(HTTPDaemon):
    def __init__(self, serverAddress, app, exact=0):
        if exact:
            address = serverAddress
        else:
            address = ('', serverAddress[1])
        HTTPDaemon.__init__(self, address)
        self.app = app
        self.server_address = serverAddress
        print "Redfoot", VERSION
        
    def run(self):
        self.start()
        try:
            while 1:        
                import threading
                threading.Event().wait(100)
        except KeyboardInterrupt:
            print "Shutting down..."
            self.stop()

    def start(self):
        servername, port = self.server_address

        handle_request = self.app.handle_request
        self.set_handle_request(handle_request)            

        HTTPDaemon.start(self)
        
        if port==80:
            print "Running at http://%s/" % servername
        else:
            print "Running at http://%s:%s/" % (servername, port)
        
    def stop(self):
        self.app.stop()
        HTTPDaemon.stop(self)

    def notify_me_of_reload(self, module):
        if module.__name__==self.module.__name__:
            self.stop()
            self.module = module            
            self.load(module)

            import sys
            sys.stderr.write("RELOADED '%s'\n" % module)
            sys.stderr.flush()


import string, sys, getopt, os
def usage():
    print """\
USAGE: run.py <options> <app name>

    options:
           [-h,--hostname <host name>]
           [-p,--port <port number>]
           [--exact]
           [--help]

    hostname
        Defaults to the computer's fully qualified name. 
    port
        Defaults to 8000.
    exact
        If exact server will listen to request coming to host via the exact host name only. Else listens to all request coming to host regaurdless of what name they come in on.
"""    
    sys.exit(-1)


if not hasattr(sys, 'version_info') or sys.version_info[0]<2:
    print """\
Can not run redfoot with Python verion:
  '%s'""" % sys.version
    print "Redfoot requires Python 2.0 or higher to run. "
    sys.exit(-1)


try:
    import threading
except ImportError:
    print """
Redfoot can not run without the threading module. Check that your PYTHONPATH is right and that you have threading.py
"""
    sys.exit(-1)
    
def command_line():
    # set default value
    port = 8000
    exact = 0
    hostname = None
    uri = None

    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'p:h:', ["help", "exact", "port=", "hostname=", "uri="])
    except getopt.GetoptError, msg:
        print msg
        usage()
    
    for optpair in optlist:
        opt, value = optpair
        if opt=="-p" or opt=="--port":
            port = string.atoi(value)
        elif opt=="-h" or opt=="--hostname":
            hostname = value
        elif opt=="--uri":
            uri = value
        elif opt=="--exact":
            exact = 1
        elif opt=="--help":
            usage()

    if not hostname:
        from socket import getfqdn
        hostname = getfqdn()

    if not uri:
        if port==80:
            uri = "http://%s/" % hostname
        else:
            uri = "http://%s:%s/" % (hostname, port)

    if len(args)!=1:
        usage()

    module = args[0]

    # Be forgiving if the module file name was specified instead of just
    # the module name
    if module[-4:] == ".xml":
        module = module[:-4]
    rd = RedDaemon((hostname, port), module, None, exact)
    rd.uri = uri
    return rd

