# -*- Mode: Python; tab-width: 4 -*-
import os, sys

from asyncore import loop

from medusa import http_server
from medusa import resolver, logger
#from medusa import filesys, default_handler

import re
# <path>;<params>?<query>#<fragment>
path_regex = re.compile (
#      path      params    query   fragment
#    r'([^;?#]*)(;[^?#]*)?(\?[^#]*)?(#.*)?'
# We are losing everything after %23's in the query string. Probably
# due to the fact that the URI has already been run through unquote? I
# think we are safe assuming it was part of the query string... do #'s
# ever make it to the server... or do the clients always deal with it?
#
#      path      params    query   
    r'([^;?#]*)(;[^?#]*)?(\?.*)?'
    )

def split_uri (uri):
    m = path_regex.match (uri)
    if m.end() != len(uri):
        raise ValueError, "Broken URI"
    else:
        _split_uri = m.groups()
    return _split_uri

class RedServer:
    def __init__(self, address, port):
        rs = None # resolver.caching_resolver ('127.0.0.1')

        lg = logger.file_logger (sys.stdout)
        self.hs = http_server.http_server (address, port, rs, lg)

        if address=='':
            address='localhost'
        print "Started server at: http://%s:%s/" % (address, port)
        sys.stdout.flush()

        #fs = filesys.os_filesystem (PUBLISHING_ROOT)
        #dh = default_handler.default_handler (fs)
        #self.hs.install_handler (dh)


    def add_handler(self, handler):
        adapter = RequestResponseAdapter(handler.handle_request)
        self.hs.install_handler(adapter)

    def remove_handler(self, handler):
        for adapter in self.hs.handlers:
            if handler==adapter._handle_request:
                self.hs.remove_handler(adapter)

    def run(self):
        become_nobody()

        # Finally, start up the server loop!  This loop will not exit until
        # all clients and servers are closed.  You may cleanly shut the system
        # down by sending SIGINT (a.k.a. KeyboardInterrupt).
        try:
            loop()
        except KeyboardInterrupt:
            print "Shut down."
        
        
def become_nobody():
    if os.name == 'posix':
        if hasattr (os, 'seteuid'):
            # look in ~medusa/patches for {set,get}euid.
            import pwd
            [uid, gid] = pwd.getpwnam ('nobody')[2:4]
            os.setegid (gid)
            os.seteuid (uid)


            #path, params, query, fragment = request.split_uri()
            path, params, query = split_uri(self.request.uri)            

            self.path = path
            self.params = (params or ';')[1:]
            self.query = (query or '?')[1:]
            
            self._handle_request(self, self)

            self.state = NEW_REQUEST
        
from cgi import parse_qs, parse_header, parse_multipart
from urllib import unquote

NEW_REQUEST, FINISH_REQUEST = [1, 2]

class RequestResponseAdapter:
    def __init__(self, handle_request):
        self._handle_request = handle_request
        self.state = NEW_REQUEST

    def match (self, request):
        return 1        

    def handle_request (self, request):
        if self.state == NEW_REQUEST:
            self._header = {}
            self.head_sent = 0
            self._new_session_uri = None        
            self.request = request        
            self.data = ''
            length = self.request.get_header('content-length')
        
            if length and length!='':
                self.request.channel.set_terminator(int(length))            
                request.collector = self
            else:
                request.collector = self
                self.state = FINISH_REQUEST

        if self.state == FINISH_REQUEST:
            request['Server'] = "Redfoot HTTP Server"
            request['Content-Type'] =  "text/html; charset=UTF-8"
            request['Connection'] =  "close"
            request['Expires'] = '-1'
            self._parameters = None
        
            #path, params, query, fragment = request.split_uri()
            path, params, query = split_uri(self.request.uri)            
            
            self.path = path
            self.params = (params or ';')[1:]
            self.query = (query or '?')[1:]
            
            self._handle_request(self, self)

            self.state = NEW_REQUEST
        
    def found_terminator (self):
        self.request.channel.set_terminator('\r\n\r\n')
        self.state = FINISH_REQUEST
        self.handle_request(self.request)

    def collect_incoming_data (self, data):
        self.data = self.data + data

    def get_header(self, name, default=''):
        return self.request.get_header(name) or default

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

    def get_path_info(self):
        return self.path

    def get_parameter(self, name, default=''):
        parameters = self.get_parameters()
        return parameters.get(name, [default,])[0]

    def get_parameters(self):
        if self._parameters==None:        
            parameters = parse_qs(self.query)
            if self.data:
                params = parse_qs(self.data)
                for param in params.keys():
                    parameters[param] = params[param]

            for parameter in parameters:
                list = parameters[parameter]
                new_list = []
                for param in list:
                    new_list.append("\n".join(param.split("\r\n")))
                parameters[parameter] = new_list
            self._parameters = parameters
        return self._parameters
        
    def set_session_uri(self, session_uri):
        self._new_session_uri = session_uri

    def _send_head(self):
        if self._new_session_uri!=None:
            import Cookie
            cookie = Cookie.SmartCookie()
            TTL = 3600*24*10000 # time to live in seconds (a long time)
            cookie['Redfoot_session'] = self._new_session_uri
            cookie['Redfoot_session']['path'] = "/"
            cookie['Redfoot_session']['Version'] = "1"
            cookie['Redfoot_session']['expires'] = Cookie._getdate(TTL)
            
            output = cookie.output()
            # Warning: Assuming there is only one header in output
            (name, value) = output.split(": ", 1)
            self.set_header(name, value)

    def set_header(self, keyword, value):
        """Send a MIME header."""
        self.request[keyword] = value

    def write(self, data):
        try:
            if self.head_sent==0:
                self.head_sent = 1
                self._send_head()
            self.request.push(data)
        except IOError:
            raise BadRequestError("write failed")                            

    def flush(self):
        try:
            if self.head_sent==0:
                self.head_sent = 1
                self._send_head()
        except IOError:
            raise BadRequestError("flush failed")
        
    def close(self):
        self.flush()
        self.request.done()        


