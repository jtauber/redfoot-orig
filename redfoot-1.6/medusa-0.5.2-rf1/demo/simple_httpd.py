# -*- Mode: Python -*-

# Create a simple HTTP server

import asyncore
from medusa import http_server

hs = http_server.http_server (
    '/usr/local/etc/httpd/docs',
    8080
    )

# Enter async main loop
asyncore.loop()




