# $Header$

from redfoot.query import QueryStore
from redfoot.editor import PeerEditor

class SampleUI:

    def __init__(self, writer, storeNode, path):
        self.writer = writer;
        self.storeNode = storeNode
        self.path = path
        self.qstore = QueryStore(storeNode)

        self.editor = PeerEditor(writer, storeNode, path)

    def setWriter(self, writer):
        self.writer = writer
        self.editor.setWriter(writer)

    def handler(self, path_info, args):
        ""

        if path_info[0:len(self.path)]==self.path:
            self.editor.handler(path_info[len(self.path):], args)
        else:
            self.view()
        # self.writer.write("unknown PATH of '%s'" % path_info)

    def view(self):
        self.writer.write("""
        <HTML>
          <HEAD>
            <TITLE>Sample UI</TITLE>
          </HEAD>
          <BODY>
            <H1>Sample UI</H1>
          </BODY>
        </HTML>
        """)

# $Log$
