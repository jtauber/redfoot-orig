from redfoot.server.http.request import Request
from redfoot.server.http.response import Response

#from redfoot.server.error import BadRequestError

#import socket

# TODO: change this to a wrapper instead...
# ... and make into SingleThreadedConnectionHandler
class HTTPConnectionHandler:

    def __init__(self, handle_request):
        self.handle_request = handle_request
        self.rr = (Request(), Response())

    def handle_connection(self, client_socket):
        try:
            request, response = self.rr
            request._set_client_socket(client_socket)
            response._set_client_socket(client_socket)
            self.handle_request(request, response)
            request.close()
            response.close()                
            client_socket.shutdown(1)
        finally:
            client_socket.close()

