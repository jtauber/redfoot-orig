from string import split, find, lower, strip
from cgi import parse_qs, parse_header, parse_multipart
from redfoot.server.error import BadRequestError

class Request:
    def __init__(self):
        pass

    def _set_client_socket(self, client_socket):
        self._rfile = client_socket.makefile('rb', 2048)
        self._firstline = None
        self._parameters = None
        self._headers = None


    def _get_first_line(self):
        if not self._firstline:
            self._firstline = self._rfile.readline()
            words = split(self._firstline)
            if len(words) == 3:
                [self._method, self._path, self._version] = words
            else:
                raise BadRequestError("Empty Request '%s'" % self._firstline)

            i = find(self._path, "?")
            if i==-1:
                self._path_info = self._path
                self._queryString = ""
            else:
                self._path_info = self._path[:i]
                self._queryString = self._path[i+1:]

        return self._firstline
    
    def get_path_info(self):
        self._get_first_line()
        return self._path_info

    def get_parameter(self, name, default=''):
        parameters = self.get_parameters()
        return parameters.get(name, [default,])[0]

    def get_header(self, name, default=''):
        headers = self.get_headers()
        return headers.get(name, default)

    def get_parameters(self):
        if self._parameters==None:
            self._get_first_line()        

            parameters = parse_qs(self._queryString)

            length = self.get_header('content-length')

            ctype, pdict = parse_header(self.get_header('content-type'))
            
            if ctype == 'multipart/form-data':
                params = parse_multipart(self._rfile, pdict)
                for param in params.keys():
                    parameters[param] = params[param]
            elif length!='':
                len = int(length)
                body = self._rfile.read(len)
                self._rfile.close()
                import cgi
                params = parse_qs(body)
                for param in params.keys():
                    parameters[param] = params[param]

            #self._parameters = Parameters(parameters)
            self._parameters = parameters

        return self._parameters

    def get_headers(self):
        if self._headers==None:
            self._get_first_line() 
            headers = {}
            line = self._rfile.readline()
            while line and not line in ('\r\n', '\n'):
                i = find(line, ':')
                if i>=0:
                    header = lower(line[:i])
                    headers[header] = strip(line[len(header)+1:])
                line = self._rfile.readline()
            #self._headers = Headers(headers)
            self._headers = headers
        return self._headers

    def get_cookies(self):
        cookieStr = self.get_header('cookie')
        
        import Cookie
        cookies = Cookie.SmartCookie()
        cookies.load(cookieStr)
        return cookies

    def get_session_uri(self):
        cookies = self.get_cookies()
        if cookies.has_key('Redfoot_session'):
            session_uri = cookies['Redfoot_session'].value            
        else:
            session_uri = None
        return session_uri

    def close(self):
        try:
            self._rfile.close()
        except IOError:
            raise BadRequestError("close failed")            


