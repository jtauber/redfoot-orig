# $Header$

from rdf.query import QueryStore
from redfoot.baseUI import BaseUI

class SampleUI(BaseUI):

    def handleRequest(self, request, response):
        args = request.parameters
        path_info = request.path_info

        if self.path_match(path_info):
            self.call_editor(request, response)
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


if __name__ == '__main__':
    import sys
    from redfoot.server import runServer
    runServer(sys.argv[1:], SampleUI)

# $Log$
