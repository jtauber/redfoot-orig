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

    def handleRequest(self, request, response):
        parameters = request.getParameters()
        headers = request.getHeaders()
        cookies = request.getCookies()

        session = request.getSession()
        if not hasattr(session, 'count'):
            session.count = 0
        else:
            session.count = session.count + 1
        
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

            response.write("<H2>Session: </H2>")
            response.write("<DL>")
            response.write("<DT>session object</DT><DD>%s</DD>" % session)
            response.write("<DT>session count</DT><DD>%s</DD>" % session.count)
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
    server.addHandler(ExampleHandler())
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
#~ Revision 3.3  2000/11/02 21:48:26  eikeon
#~ removed old log messages
#~
# Revision 3.2  2000/10/31 05:03:07  eikeon
# mainly Refactored how parameters are accessed (no more [0]'s); some cookie code; a few minor changes regaurding plumbing
#
# Revision 3.1  2000/10/27 16:20:02  eikeon
# small cleanup... mostly formatting
#
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
