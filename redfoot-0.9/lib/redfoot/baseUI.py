# $Header$

from rdf.query import QueryStore
from redfoot.editor import PeerEditor

class BaseUI:

    def __init__(self, storeNode, path):
        self.storeNode = storeNode
        self.path = path
#        self.qstore = QueryStore(storeNode)
        self.qstore = storeNode
        self.editor = None


    def getEditor(self):
        if self.editor==None:
            self.editor = PeerEditor(self.storeNode, self.path)
        return self.editor

    def path_match(self, path_info):
        return path_info[0:len(self.path)]==self.path

    def call_editor(self, request, response):
        request._pathInfo = request.getPathInfo()[len(self.path):]
        self.getEditor().handle_request(request, response)

#~ $Log$
#~ Revision 5.1  2000/12/17 23:41:58  eikeon
#~ removed of log messages
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
