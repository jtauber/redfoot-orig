# $Header$

from redfoot.query import QueryStore
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

    def call_editor(self, path_info, args):
        self.editor.handler(path_info[len(self.path):], args)

# $Log$

