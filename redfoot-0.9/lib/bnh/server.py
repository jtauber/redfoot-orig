# $Header$

"""
eikeon's Bare Naked HTTP Server
"""

__version__ = "$Revision$"

import socket
import sys
import string


class Server:
    ""

    def __init__(self, server_address):
        ""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        self.socket.bind(server_address)
        self.socket.listen(5)

        from Queue import Queue
        self.queue = Queue(5)

    def _acceptRequests(self):
        while 1:
            try:
                clientSocket, client_address = self.socket.accept()
            except socket.error:
                #TODO: log
                break

            try:
                self.queue.put(clientSocket)
            except:
                #TODO: log
                break

    def start(self):
        sys.stderr.write("Started eikeon's Bare Naked HTTP Server.\n")
        sys.stderr.flush()
        import threading
        t = threading.Thread(target = self._acceptRequests, args = ())
        t.setDaemon(1)
        t.start()


    def addHandler(self, handler):
        class Handler:
            def __init__(self, server, handler):
                self.server = server
                self.handler = ServerConnection(handler)
        
            def start(self):
                while 1:
                    #sys.stderr.write("handling request\n")
                    #sys.stderr.flush()
            
                    clientSocket = self.server.queue.get()
                    self.handler.handleRequest(self.server, clientSocket)
    
        
        handler = Handler(self, handler)
        import threading
        t = threading.Thread(target = handler.start, args = ())
        t.setDaemon(1)
        t.start()


        
class ServerConnection:

    def __init__(self, handler):
        self.request = Request()
        self.response = Response()
        self.handler = handler
        
    def handleRequest(self, server, clientSocket):

        try:
            try:
                self.request.setClientSocket(clientSocket)
                self.response.setClientSocket(clientSocket)
                self.handler.handleRequest(self.request, self.response)
                self.response.close()
                clientSocket.shutdown(1)
            finally:
                clientSocket.close()
        except socket.error:
            #TODO: log
            pass
        except BadRequestError:
            #TODO: log
            pass
        except:
            import traceback
            traceback.print_exc()



class Error:
    def __init__(self, msg=''):
        self._msg = msg
    def __repr__(self):
        return self._msg

class BadRequestError(Error):
    def __init__(self, msg):
        Error.__init__(self, "%s" % msg)
        self.message = msg

class Request:
    
    def setClientSocket(self, clientSocket):
        rfile = clientSocket.makefile('rb', 0)

        firstline = rfile.readline()

        words = string.split(firstline)
        if len(words) == 3:
            [self.method, self.path, self.version] = words
        else:
            raise BadRequestError("Empty Request '%s'" % firstline)

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

        # TODO: look into char encoding issues at some point in time
        #from encodings.utf_8 import StreamWriter
        #self.wfile = StreamWriter(self.wfile)
        
        self.write("%s %s %s\r\n" % ("HTTP/1.1", "200", "OK"))
        self.send_header('Server', "eikeon's Bare Naked HTTP Server")
        self.send_header('Date', date_time_string())
        self.send_header('Expires', "-1")
        self.send_header('Connection', "close")
        self.write("\r\n")

    
    def send_header(self, keyword, value):
        """Send a MIME header."""

        self.write("%s: %s\r\n" % (keyword, value))


    def write(self, str):
        try:
            self.wfile.write(str)
        except IOError:
            raise BadRequestError("write failed")            

    def flush(self):
        try:
            self.wfile.flush()
        except IOError:
            raise BadRequestError("flush failed")
        
    def close(self):
        try:
            self.wfile.flush()
            self.wfile.close()
        except IOError:
            raise BadRequestError("close failed")            

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
# Revision 1.5  2000/10/26 19:40:44  eikeon
# Added TODO: stating we should look at char encoding issues at some point in time
#
# Revision 1.4  2000/10/26 03:39:03  eikeon
# one line :)
#
# Revision 1.3  2000/10/26 01:18:36  eikeon
# changed interface to server and dependant code
#
# Revision 1.2  2000/10/25 21:59:47  eikeon
# catching more exceptions caused by connection reset by peer etc and re throwing them as BadRequestError
#
# Revision 1.1  2000/10/25 20:40:31  eikeon
# changes relating to new directory structure
#
# Revision 2.2  2000/10/18 20:02:23  eikeon
# added eikeon's
#
# Revision 2.1  2000/10/17 18:33:43  eikeon
# Yet again... better exception handling; No longer prints out tracebacks of 'non fatal' exceptions
#
# Revision 2.0  2000/10/14 01:13:34  jtauber
# next version
#
# Revision 1.5  2000/10/13 22:19:47  eikeon
# catching all exceptions so that server does not hang
#
# Revision 1.4  2000/10/13 05:03:10  eikeon
# catching a few more exception
#
# Revision 1.3  2000/10/13 04:45:27  eikeon
# changed Server header value
#
# Revision 1.2  2000/10/13 04:25:35  eikeon
# fixed startup message
#
# Revision 1.1.1.1  2000/10/13 03:59:06  eikeon
# initial import
#
