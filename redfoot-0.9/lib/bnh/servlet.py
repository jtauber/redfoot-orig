import socket
import sys
import time
import string

from threading import RLock
from threading import Condition

class Cubby:

    def __init__(self):
        self.mon = RLock()
        self.rc = Condition(self.mon)
        self.wc = Condition(self.mon)
        self.queue = []

    def put(self, item):
        self.mon.acquire()
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

    def peek(self):
        self.mon.acquire()
        if not self.queue:
            item = None
        else:
            item = self.queue[0]
        self.mon.release()
        return item

    def wait(self, timeout=None):
        self.mon.acquire()
        self.rc.wait(timeout)
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
        self.cubby = Cubby()
        import threading
        t = threading.Thread(target = self._sessionReaper, args = ())
        t.setDaemon(1)
        t.start()

    def _sessionReaper(self):
        while 1:
            sessionKey = self.cubby.peek()
            if sessionKey==None:
                self.cubby.wait(1)
            else:
                import time
                now = time.time()
                session = self.sessions[sessionKey]
                
                idle = (now - session.getLastAccessedTime())
                if idle > session.getMaxInactiveInterval():
                    self.cubby.get() # todo... pop
                    del self.sessions[sessionKey]
                else:
                    delta = session.getMaxInactiveInterval() -  idle
                    self.cubby.wait(delta)
                    
class Session:
    def __init__(self, id):
        now = time.time()
        self._creationTime = now
        self._setLastAccessedTime(now)
        self._attributes = {}
        self.maxInactiveInterval = 30 * 60 # default to 30 minutes
        self._id = id

    def getAttribute(self, name):
        if self._attributes.has_key(name):
            return self._attributes[name]
        else:
            return None
    
    def getAttributeNames(self):
        return self._attributes.keys()
    
    def getCreationTime(self):
        return self._creationTime

    def getId(self):
        return self._id

    def getLastAccessedTime(self):
        return self._lastAccessedTime

    def _setLastAccessedTime(self, time):
        self._lastAccessedTime = time

    def getMaxInactiveInterval(self):
        return self.maxInactiveInterval

    def setMaxInactiveInterval(self, interval):
        self._maxInactiveInterval = interval

    def invalidate(self):
        self._invalid = 1

    def isNew(self):
        return self.new==1

    def removeAttribute(self, name):
        del self.attributes[name]

    def setAttribute(self, name, value):
        self.attributes[name] = value

    def setMaxInactiveInterval(self, interval):
        self._maxInactiveInterval = interval
    


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
            sessionKey = cookies['EBNH_session'].value
            if sessions.has_key(sessionKey):
                session = sessions[sessionKey]
                session._setLastAccessedTime(time.time())
                return session

        # Create a new session
        from whrandom import random
        rn = random()
        session = "%s#T%s" % (rn, time.time())
        self.connection.session = session

        if sessions.has_key(session):
            raise "TODO: exception"

        sessions[session] = Session(session)

        self.connection.context.cubby.put(session)

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

        TTL = 60*60*24 # time to live in seconds
        expire = time.time()+TTL

        if hasattr(self.connection, 'session'):
            if self.connection.session!=None:
                cookie['EBNH_session'] = self.connection.session
                cookie['EBNH_session']['path'] = "/"
                cookie['EBNH_session']['Version'] = "1"
                cookie['EBNH_session']['expires'] = date_time_string(expire)
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


def date_time_string(t=None):
    """Return the current date and time formatted for a message header."""
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    if t==None:
        t = time.time()

    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % ( weekdayname[wd], day, monthname[month], year, hh, mm, ss)
    return s


