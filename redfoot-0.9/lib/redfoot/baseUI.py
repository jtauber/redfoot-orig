# $Header$

from rdf.query import QueryStore
from redfoot.editor import PeerEditor

class BaseUI:

    def __init__(self, writer, storeNode, path):
        self.writer = writer;
        self.storeNode = storeNode
        self.path = path
        self.qstore = QueryStore(storeNode)

        self.editor = PeerEditor(writer, storeNode, path)

    def setWriter(self, writer):
        self.writer = writer
        self.editor.setWriter(writer)

    def path_match(self, path_info):
        return path_info[0:len(self.path)]==self.path

    def call_editor(self, request, response):
        request.path_info = request.path_info[len(self.path):]
        self.editor.handleRequest(request, response)

#~ $Log$
# Revision 3.1  2000/10/31 05:03:08  eikeon
# mainly Refactored how parameters are accessed (no more [0]'s); some cookie code; a few minor changes regaurding plumbing
#
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
