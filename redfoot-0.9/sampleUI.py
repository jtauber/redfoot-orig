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
        elif path_info=="/":
            self.main()
        else:
            self.view()
        # self.writer.write("unknown PATH of '%s'" % path_info)

    def main(self):
        self.writer.write("""
        <HTML>
          <HEAD>
            <TITLE>Main Page</TITLE>
          </HEAD>
          <BODY>
            <H1>Main Page</H1>
            <UL>
        """)
        for s in self.qstore.get(None, QueryStore.TYPE, "http://redfoot.sourceforge.net/2000/10/#Person"):
            self.writer.write("<LI>%s</LI>" % self.qstore.label(s[0]))
        self.writer.write("""
            </UL>
            <P><A HREF="%s/classList">Go to editor</A>
          </BODY>
        </HTML>
        """% self.path)

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
# Revision 1.2  2000/10/17 03:42:45  jtauber
# included rdf file for sample ui and added a page that does a query
#
# Revision 1.1  2000/10/17 02:31:10  jtauber
# beginnings of a sample UI
#
