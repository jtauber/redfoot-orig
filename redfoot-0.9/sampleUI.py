# $Header$

from redfoot.query import QueryStore
from redfoot.baseUI import BaseUI

class SampleUI(BaseUI):

    def handler(self, path_info, args):
        ""

        if self.path_match(path_info):
            self.call_editor(path_info, args)
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
            <P>These are the people I know about:</P>
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
# Revision 1.3  2000/10/19 00:33:07  jtauber
# sample ui now links to peer editor
#
# Revision 1.2  2000/10/17 03:42:45  jtauber
# included rdf file for sample ui and added a page that does a query
#
# Revision 1.1  2000/10/17 02:31:10  jtauber
# beginnings of a sample UI
#




