# $Header$

"""
Example request handling and invocation code for eikeon's Bare Naked HTTP Server.
"""

__version__ = "$Revision$"

from bnh.server import Server, ServerConnection
import string


class ExampleHandler:

    def __init__(self):
        import threading
        self.lock = threading.Lock()
        self.viewer = None

    def handleRequest(self, request, response):
        args = request.parameters
        path_info = request.path_info

        self.lock.acquire()
        try:
            response.write("""
<HTML>
<HEAD>
<TITLE>Example</TITLE>
</HEAD>
<BODY>
<H1>Example</H1>
""")

            response.write("<H2>Args:</H2>")
            response.write("<DL>")
            for arg in args.keys():
                response.write("<DT>%s</DT><DD>%s</DD>" % (arg, args[arg]))
            response.write("</DL>")
            response.write("""
</BODY>
</HTML>
""")
        finally:
            self.lock.release()            


class ExampleServerConnection(ServerConnection):

    handler = ExampleHandler()

    def __init__(self):
        ServerConnection.__init__(self, None)
        self.handler = ExampleServerConnection.handler
        

if __name__ == '__main__':

    # set default value
    port = 8000
        
    import sys
    import getopt
    optlist, args = getopt.getopt(sys.argv[1:], 'p:')
    for optpair in optlist:
        opt, value = optpair
        if opt=="-p":
            port = string.atoi(value)
            
    server = Server(('', port), lambda : ExampleServerConnection())
    
    import threading
    t = threading.Thread(target = server.start, args = ())
    t.setDaemon(1)
    t.start()

    sys.stderr.write("EXAMPLE: serving requests on port %s...\n" % port)
    sys.stderr.flush()

    while 1:
        try:
            threading.Event().wait(100)
        except KeyboardInterrupt:
            sys.exit()


# $Log$
