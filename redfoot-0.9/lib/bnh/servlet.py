# $Header$
import socket
import sys
import time
import string

class ServerConnection:

    def __init__(self, handler):
        self.request = Request(self)
        self.response = Response(self)
        self.handler = handler

    def handle_request(self, server, client_socket):
        try:
            try:
                self.request._set_client_socket(client_socket)
                self.response._set_client_socket(client_socket)
                self.handler.handle_request(self.request, self.response)
                self.request.close()
                self.response.close()                
                client_socket.shutdown(1)
            finally:
                client_socket.close()
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
    def __init__(self, connection):
        self.connection = connection

    def _set_client_socket(self, client_socket):
        self._rfile = client_socket.makefile('rb', 0)
        self._firstline = None
        self._parameters = None
        self._headers = None


    def _get_first_line(self):
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
        self._get_first_line()
        return self._pathInfo

    def setPathInfo(self, pathInfo):
        self._pathInfo = pathInfo

    def getParameters(self):
        if self._parameters==None:
            self._get_first_line()        

            import cgi
            parameters = cgi.parse_qs(self._queryString)

            length = self.getHeaders()['content-length']

            ctype, pdict = cgi.parse_header(self.getHeaders()['content-type'])
            
            if ctype == 'multipart/form-data':
                sys.stderr.write("MULTI\n")
                sys.stderr.flush()

                params = cgi.parse_multipart(self._rfile, pdict)
                for param in params.keys():
                    parameters[param] = params[param]
            elif length!='':
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

    def get_session_uri(self):
        cookies = self.getCookies()
        if cookies.has_key('EBNH_session'):
            session_uri = cookies['EBNH_session'].value            
        else:
            session_uri = None
        return session_uri

    def close(self):
        try:
            self._rfile.close()
        except IOError:
            raise BadRequestError("close failed")            


class Response:

    def __init__(self, connection):
        self.connection = connection

    def _set_client_socket(self, client_socket):
        self._wfile = client_socket.makefile('wb', 0)
        self.head_sent = 0
        self._header = {'Server': "eikeon's Bare Naked HTTP Server",
                       'Date': date_time_string(),
                       'Expires': "-1",
                       'Content-Type': "text/html",
                       'Connection': "close" }
        self._new_session_uri = None
            
        
    def set_session_uri(self, session_uri):
        self._new_session_uri = session_uri

    def _send_head(self):
        self.write("%s %s %s\r\n" % ("HTTP/1.1", "200", "OK"))

        for key in self._header.keys():
            self.write("%s: %s\r\n" % (key, self._header[key]))

        if self._new_session_uri!=None:
            import Cookie
            cookie = Cookie.SmartCookie()
            TTL = 3600*24*10000 # time to live in seconds (a long time)
            cookie['EBNH_session'] = self._new_session_uri
            cookie['EBNH_session']['path'] = "/"
            cookie['EBNH_session']['Version'] = "1"
            cookie['EBNH_session']['expires'] = Cookie._getdate(TTL)
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


#~ $Log$
#~ Revision 7.1  2001/04/03 03:15:43  eikeon
#~ added get_session_uri method
#~
#~ Revision 7.0  2001/03/26 23:41:04  eikeon
#~ NEW RELEASE
#~
#~ Revision 6.2  2001/03/26 20:19:01  eikeon
#~ removed old header
#~
#~ Revision 6.1  2001/03/13 04:02:50  eikeon
#~ fixed cookies so that they persist a very long time; changed default max inactive time to 10 years
#~
#~ Revision 6.0  2001/02/19 05:01:23  jtauber
#~ new release
