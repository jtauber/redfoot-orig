from redfoot.server.error import BadRequestError

class Response:

    def __init__(self):
        pass

    def _set_client_socket(self, client_socket):
        self._wfile = client_socket.makefile('wb', 4096)
        self.head_sent = 0
        self._header = {'Server': "Redfoot HTTP Server",
                       'Date': _date_time_string(),
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
            cookie['Redfoot_session'] = self._new_session_uri
            cookie['Redfoot_session']['path'] = "/"
            cookie['Redfoot_session']['Version'] = "1"
            cookie['Redfoot_session']['expires'] = Cookie._getdate(TTL)
            self.write(cookie.output())

        self.write("\r\n")

    
    def set_header(self, keyword, value):
        """Send a MIME header."""
        self._header[keyword] = value


    def write(self, str):
        try:
            if self.head_sent==0:
                self.head_sent = 1
                self._send_head()
                
            self._wfile.write(str.encode('Latin-1', 'replace'))
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



import time

_last_time = -1
def _date_time_string():
    """Returns date / time for the 'Date' HTTP header accurate to about a second."""
    
    t = time.time()
    global _last_time, _last_time_string
    if (t - _last_time)>1:
        _last_time = t
        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
        _last_time_string = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % ( ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][wd], day, [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month], year, hh, mm, ss)
    return _last_time_string
