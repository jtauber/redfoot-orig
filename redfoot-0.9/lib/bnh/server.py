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
        self.server_address = server_address
        self.handlerCubby = HandlerCubby(5)

    def _acceptRequests(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        self.socket.bind(self.server_address)
        self.socket.listen(5)
        while 1:
            try:
                clientSocket, client_address = self.socket.accept()
                self.handlerCubby.put(clientSocket)
            except socket.error:
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
                context = ServerContext()
                self.handler = ServerConnection(handler, context)
                self.running = 1
        
            def start(self):
                handlerCubby = self.server.handlerCubby
                while self.running==1:
                    clientSocket = handlerCubby.get()
                    if clientSocket!=None:
                        self.handler.handleRequest(self.server, clientSocket)
                    else:
                        handlerCubby.wait()

            def stop(self):
                self.server.handlerCubby.stop(self)

        handler = Handler(self, handler)
        import threading
        t = threading.Thread(target = handler.start, args = ())
        t.setDaemon(1)
        t.start()
        return handler


from threading import RLock
from threading import Condition

class HandlerCubby:

    def __init__(self, limit):
        self.mon = RLock()
        self.rc = Condition(self.mon)
        self.wc = Condition(self.mon)
        self.limit = limit
        self.queue = []

    def put(self, item):
        self.mon.acquire()
        while len(self.queue) >= self.limit:
            self.wc.wait()
        self.queue.append(item)
        self.rc.notify()
        self.mon.release()

    def get(self):
        self.mon.acquire()
        if not self.queue:
            item = None
        else:
            item = self.queue[0]
            del self.queue[0]
            self.wc.notify()
        self.mon.release()
        return item

    def wait(self):
        self.mon.acquire()
        self.rc.wait()
        self.mon.release()

    def stop(self, handler):
        self.mon.acquire()
        handler.running = 0
        self.rc.notifyAll()
        self.mon.release()
    

class ServerConnection:

    def __init__(self, handler, context):
        self.request = Request(self)
        self.response = Response(self)
        self.handler = handler
        self.context = context
        
    def handleRequest(self, server, clientSocket):
        try:
            try:
                self.request._setClientSocket(clientSocket)
                self.response._setClientSocket(clientSocket)
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


class ServerContext:
    def __init__(self):
        self.sessions = {}

class Session:
    pass


class Request:
    def __init__(self, connection):
        self.connection = connection

    def _setClientSocket(self, clientSocket):
        self._rfile = clientSocket.makefile('rb', 0)
        self._firstline = None
        self._parameters = None
        self._headers = None


    def _getFirstLine(self):
        if not self._firstline:
            self._firstline = self._rfile.readline()
            words = string.split(self._firstline)
            if len(words) == 3:
                [self._method, self._path, self._version] = words
            else:
                raise BadRequestError("Empty Request '%s'" % self._firstline)

            i = string.find(self._path, "?")
            if i==-1:
                self._pathInfo = self._path
                self._queryString = ""
            else:
                self._pathInfo = self._path[:i]
                self._queryString = self._path[i+1:]

        return self._firstline
    
    def getPathInfo(self):
        self._getFirstLine()
        return self._pathInfo

    def setPathInfo(self, pathInfo):
        self._pathInfo = pathInfo

    def getParameters(self):
        if self._parameters==None:
            self._getFirstLine()        

            import cgi
            parameters = cgi.parse_qs(self._queryString)

            length = self.getHeaders()['content-length']
            if length!='':
                len = int(length)
                body = self._rfile.read(len)
                self._rfile.close()
                import cgi
                params = cgi.parse_qs(body)
                for param in params.keys():
                    parameters[param] = params[param]

            self._parameters = Parameters(parameters)

        return self._parameters

    def getHeaders(self):
        if self._headers==None:
            headers = {}
            line = self._rfile.readline()
            while line and not line in ('\r\n', '\n'):
                i = string.find(line, ':')
                if i<0:
                    continue
                header = string.lower(line[:i])
                headers[header] = string.strip(line[len(header)+1:])
                line = self._rfile.readline()
            self._headers = Headers(headers)
        return self._headers

    def getCookies(self):
        cookieStr = self.getHeaders()['cookie']
        
        import Cookie
        cookies = Cookie.SmartCookie()
        cookies.load(cookieStr)
        return cookies

    def getSession(self):
        self.connection.session = None
        
        sessions = self.connection.context.sessions
        cookies = self.getCookies()

        if cookies.has_key('EBNH_session'):
            session = cookies['EBNH_session'].value
            if sessions.has_key(session):
                return sessions[session]

        # Create a new session
        from whrandom import random
        rn = random()
        import time
        session = "%s#T%s" % (rn, time.time())
        self.connection.session = session

        if sessions.has_key(session):
            raise "TODO: exception"

        sessions[session] = Session()

        return sessions[session]


class Response:

    def __init__(self, connection):
        self.connection = connection

    def _setClientSocket(self, clientSocket):
        self._wfile = clientSocket.makefile('wb', 0)
        self.head_sent = 0
        self._header = {'Server': "eikeon's Bare Naked HTTP Server",
                       'Date': date_time_string(),
                       'Expires': "-1",
                       'Content-Type': "text/html",
                       'Connection': "close" }
            
        
    def _send_head(self):
        self.write("%s %s %s\r\n" % ("HTTP/1.1", "200", "OK"))

        for key in self._header.keys():
            self.write("%s: %s\r\n" % (key, self._header[key]))

        import Cookie
        cookie = Cookie.SmartCookie()
        if hasattr(self.connection, 'session'):
            if self.connection.session!=None:
                cookie['EBNH_session'] = self.connection.session
                cookie['EBNH_session']['path'] = "/"
                cookie['EBNH_session']['Version'] = "1"
        self.write(cookie.output())

        self.write("\r\n")

    
    def setHeader(self, keyword, value):
        """Send a MIME header."""
        self._header[keyword] = value


    def write(self, str):
        try:
            if self.head_sent==0:
                self.head_sent = 1
                self._send_head()
                
            self._wfile.write(str)
        except IOError:
            raise BadRequestError("write failed")            

    def flush(self):
        try:
            self._wfile.flush()
        except IOError:
            raise BadRequestError("flush failed")
        
    def close(self):
        try:
            self._wfile.flush()
            self._wfile.close()
        except IOError:
            raise BadRequestError("close failed")            


from UserDict import UserDict

class Parameters(UserDict):
    def __getitem__(self, key):
        if self.data.has_key(key):
            list = self.data[key]
            if not len(list)==1:
                "Parameter does not have exactly one value"
            return list[0]
        else:
            return ""

class Headers(UserDict):
    def __getitem__(self, key):
        if self.data.has_key(key):
            return self.data[key]
        else:
            return ""


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


#~ $Log$
#~ Revision 3.5  2000/11/03 23:04:08  eikeon
#~ Added support for cookies and sessions; prefixed a number of methods and variables with _ to indicate they are private; changed a number of methods to mixed case for consistency; added a setHeader method on response -- headers where hardcoded before; replaced writer with response as writer predates and is redundant with repsonse; Added authentication to editor
#~
#~ Revision 3.4  2000/11/03 19:52:00  eikeon
#~ first pass at sessions... needs cleanup
#~
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
