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
                self.queue.put(clientSocket)
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
        
            def start(self):
                while 1:
                    clientSocket = self.server.queue.get()
                    self.handler.handleRequest(self.server, clientSocket)
        
        handler = Handler(self, handler)
        import threading
        t = threading.Thread(target = handler.start, args = ())
        t.setDaemon(1)
        t.start()


class ServerConnection:

    def __init__(self, handler, context):
        self.request = Request(self)
        self.response = Response(self)
        self.handler = handler
        self.context = context
        
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


class ServerContext:

    def __init__(self):
        self.sessions = {}

class Session:
    pass


class Request:

    def __init__(self, connection):
        self.connection = connection

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
            parameters = {}
        else:
            self.path_info = self.path[:i]
            self.query_string = self.path[i+1:]
            import cgi
            parameters = cgi.parse_qs(self.query_string)

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
                parameters[param] = params[param]

        self.parameters = Parameters(parameters)
        self.headers = Headers(headers)


    def getParameters(self):
        return self.parameters

    def getHeaders(self):
        return self.headers

    def getCookies(self):
        cookieStr = self.headers['cookie']
        
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

    def setClientSocket(self, clientSocket):
        self.wfile = clientSocket.makefile('wb', 0)

        self.write("%s %s %s\r\n" % ("HTTP/1.1", "200", "OK"))
        self.send_header('Server', "eikeon's Bare Naked HTTP Server")
        self.send_header('Date', date_time_string())
        self.send_header('Expires', "-1")
        self.send_header('Connection', "close")
        import Cookie
        cookie = Cookie.SmartCookie()
        if hasattr(self.connection, 'session'):
            if self.connection.session!=None:
                cookie['EBNH_session'] = self.connection.session
                cookie['EBNH_session']['path'] = "/"
                cookie['EBNH_session']['Version'] = "1"
        self.write(cookie.output())

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
