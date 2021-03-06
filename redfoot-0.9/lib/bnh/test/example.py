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

    def handle_request(self, request, response):
        parameters = request.get_parameters()
        headers = request.get_headers()
        cookies = request.get_cookies()

        session_uri = request.get_session_uri()

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

            response.write("<H2>Session: </H2>")
            response.write("<DL>")
            response.write("<DT>session uri</DT><DD>%s</DD>" % session_uri)
            response.write("</DL>")            
                
            response.write("<H2>Parameters:</H2>")
            response.write("<DL>")
            for arg in parameters.keys():
                response.write("<DT>%s</DT><DD>%s</DD>" % (arg, parameters[arg]))
            response.write("</DL>")

            response.write("<H2>Headers:</H2>")
            response.write("<DL>")
            for arg in headers.keys():
                response.write("<DT>%s</DT><DD>%s</DD>" % (arg, headers[arg]))
            response.write("</DL>")

            response.write("<H2>Cookies:</H2>")
            response.write("<DL>")
            for arg in cookies.keys():
                response.write("<DT>%s</DT><DD>%s</DD>" % (arg, cookies[arg].value))
            response.write("</DL>")

            response.write("""
</BODY>
</HTML>
""")
        finally:
            self.lock.release()            


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
            
    server = Server(('', port))
    server.set_handler(ExampleHandler())
    server.start()

    sys.stderr.write("EXAMPLE: serving requests on port %s...\n" % port)
    sys.stderr.flush()

    while 1:
        try:
            import threading
            threading.Event().wait(100)
        except KeyboardInterrupt:
            sys.exit()


#~ $Log$
#~ Revision 8.0  2001/04/27 00:52:13  eikeon
#~ new release
