# $Header$

__version__ = "$Revision$"

from redfoot.server.http.handler import Handler


class ExampleHandler(Handler):

    def __init__(self):
        Handler.__init__(self)
        import threading
        #self.lock = threading.Lock()

    def handle(self):
        request, response = (self.request, self.response)
        
        parameters = request.get_parameters()
        headers = request.get_headers()
        cookies = request.get_cookies()

        session_uri = request.get_session_uri()

        #self.lock.acquire()
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
            pass
            #self.lock.release()            


import string
from redfoot.server.daemon import Daemon

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
            
    daemon = Daemon(('', port))
    daemon.set_handle_connection(ExampleHandler().handle_connection)
    daemon.start()
    daemon.stop()
    daemon.set_handle_connection(ExampleHandler().handle_connection)    
    daemon.start()

    sys.stderr.write("EXAMPLE: serving requests on port %s...\n" % port)
    sys.stderr.flush()


    try:
        while 1:        
            import threading
            threading.Event().wait(100)
    except KeyboardInterrupt:
        daemon.stop()


#~ $Log$
#~ Revision 6.0  2001/09/04 05:30:33  eikeon
#~ NEW RELEASE
#~
#~ Revision 5.0  2001/08/28 04:04:11  eikeon
#~ NEW RELEASE
#~
#~ Revision 4.0  2001/08/21 22:09:52  eikeon
#~ NEW RELEASE
#~
#~ Revision 3.0  2001/08/15 05:39:04  eikeon
#~ NEW RELEASE
#~
#~ Revision 2.0  2001/08/15 04:28:11  eikeon
#~ NEW RELEASE
#~
#~ Revision 1.1.1.1  2001/08/14 22:29:57  eikeon
#~ TRANSFER FROM EIKCO
#~
#~ Revision 1.6  2001/08/11 17:22:28  jtauber
#~ removed references to bnh
#~
#~ Revision 1.5  2001/06/21 20:02:22  dkrech
#~ *** empty log message ***
#~
#~ Revision 1.4  2001/06/20 17:13:49  dkrech
#~ *** empty log message ***
#~
#~ Revision 1.3  2001/06/20 01:21:09  dkrech
#~ renamed default to daemon
#~
#~ Revision 1.2  2001/06/17 20:16:57  dkrech
#~ initial
#~
#~ Revision 1.1  2001/06/15 19:40:00  dkrech
#~ init checkin of rewriten server support
#~
#~ Revision 8.1  2001/04/29 03:25:11  eikeon
#~ more getXxx -> get_xxx
#~
#~ Revision 8.0  2001/04/27 00:52:13  eikeon
#~ new release
