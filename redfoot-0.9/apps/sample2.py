# $Header$

from rdf.query import QueryStore
from redfoot.rednode import RedNode
from redfoot.editor import Editor

from rdf.const import *

import sys

class Sample2(Editor):

    def __init__(self, rednode):
        self.storeNode = rednode
        Editor.__init__(self, rednode)

    def handle_request(self, request, response):
        path_info = request.getPathInfo()

        sys.stderr.write("path_info: %s" % path_info)
        sys.stderr.write("headers: %s" % request.getHeaders())
        sys.stderr.flush()

        if request.getHeaders()['accept-language']=='rdf':
            sys.stderr.write("got it")
            sys.stderr.flush()

            node = self.storeNode.local.journal
            node.output(response, None, None, None, None)

        if path_info=="journal":
            node = self.storeNode.local.journal
            node.output(response, None, None, None, None)
        else:
            Editor.handle_request(self, request, response)

            

