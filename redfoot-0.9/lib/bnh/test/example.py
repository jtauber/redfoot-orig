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
        parameters = request.getParameters()
        headers = request.getHeaders()
        cookies = request.getCookies()

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
#~ Revision 7.1  2001/04/12 22:52:18  eikeon
#~ removed management of session objects; BNH now only deals with the setting/getting of the EBNH_session cookie
#~
#~ Revision 7.0  2001/03/26 23:41:04  eikeon
#~ NEW RELEASE
#~
#~ Revision 6.1  2001/03/26 20:19:00  eikeon
#~ removed old header
#~
#~ Revision 6.0  2001/02/19 05:01:23  jtauber
#~ new release
