# -*- Mode: Python -*-

# This is something you might want to use on a machine running Windows
# NT or Windows 95 - simultaneously publish the directory 'd:/public'
# via http and ftp, on the standard ports.

import asyncore
from medusa import http_server
from medusa import ftp_server

# Change this path to publish a different directory
DIRECTORY = 'd:/public'

hs = http_server.http_server(DIRECTORY, 80)

fs = ftp_server.ftp_server(ftp_server.dummy_authorizer(DIRECTORY),
                           port = 21
                           )

# Run the async main loop
asyncore.loop()

