# $Header$

"""
Bare Naked HTTP Server
"""

__version__ = "$Revision$"

import socket
import sys
import string


class Server:
    ""

    def __init__(self, server_address, serverConnectionFactory):
        ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        self.socket.bind(server_address)
        self.socket.listen(5)
        self.serverConnectionFactory = serverConnectionFactory

    def start(self):
        sys.stderr.write("Started eikeon's Bare Naked HTTP Server.\n")
        sys.stderr.flush()
        
        while 1:
            try:
                clientSocket, client_address = self.socket.accept()
            except socket.error:
                break

            try:
                sc = apply(self.serverConnectionFactory, ())
                import threading
                t = threading.Thread(target = sc.handleRequest,
                                     args = (self, clientSocket))
                t.start()
            except:
                import traceback
                traceback.print_exc()
                

        
class ServerConnection:

    def __init__(self, handler):
        self.request = Request()
        self.response = Response()
        self.handler = handler
        
    def handleRequest(self, server, clientSocket):

        try:
            self.request.setClientSocket(clientSocket)
            self.response.setClientSocket(clientSocket)
            self.handler.handleRequest(self.request, self.response)
        except:
            import traceback
            traceback.print_exc()
            
        self.response.close()
        clientSocket.shutdown(1)
        clientSocket.close()


class Request:
    
    def setClientSocket(self, clientSocket):
        rfile = clientSocket.makefile('rb', 0)

        firstline = rfile.readline()

        sys.stderr.write("FIRSTLINE: %s" % firstline)
        sys.stderr.flush()

        words = string.split(firstline)
        if len(words) == 3:
            [self.method, self.path, self.version] = words
        else:
            sys.stderr.write("Warning: ignoring the request '%s'" % firstline)
            sys.stderr.flush()

        i = string.find(self.path, "?")
        if i==-1:
            self.path_info = self.path
            self.query_string = ""
            self.parameters = {}
        else:
            self.path_info = self.path[:i]
            self.query_string = self.path[i+1:]
            import cgi
            self.parameters = cgi.parse_qs(self.query_string)

        headers = {}
        line = rfile.readline()
        while line and not line in ('\r\n', '\n'):
            i = string.find(line, ':')
            if i<0:
                continue
            header = string.lower(line[:i])
            headers[header] = string.strip(line[len(header)+1:])
            line = rfile.readline()

        if headers.has_key('content-length'):
            cLen = int(headers['content-length'])
            body = rfile.read(cLen)
            rfile.close()
            import cgi
            params = cgi.parse_qs(body)
            for param in params.keys():
                self.parameters[param] = params[param]


class Response:

    def setClientSocket(self, clientSocket):
        self.wfile = clientSocket.makefile('wb', 0)        

        self.wfile.write("%s %s %s\r\n" % ("HTTP/1.1", "200", "OK"))
        self.send_header('Server', "eikeon's Bare Naked HTTP Server")
        self.send_header('Date', date_time_string())
        self.send_header('Expires', "-1")
        self.send_header('Connection', "close")
        self.wfile.write("\r\n")

    
    def send_header(self, keyword, value):
        """Send a MIME header."""

        self.wfile.write("%s: %s\r\n" % (keyword, value))


    def write(self, str):
        self.wfile.write(str)

    def flush(self):
        self.wfile.flush()

    def close(self):
        self.wfile.flush()
        self.wfile.close()
        

def date_time_string():
    """Return the current date and time formatted for a message header."""

    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    import time
    now = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(now)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        weekdayname[wd],
        day, monthname[month], year,
        hh, mm, ss)
    return s


# $Log$
# Revision 1.3  2000/10/13 04:45:27  eikeon
# changed Server header value
#
# Revision 1.2  2000/10/13 04:25:35  eikeon
# fixed startup message
#
# Revision 1.1.1.1  2000/10/13 03:59:06  eikeon
# initial import
#
