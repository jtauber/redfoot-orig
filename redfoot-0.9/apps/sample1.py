# $Header$

from redfoot.server import RedServer
from redfoot.rednode import RedNode
from redfoot.editor import Editor
from rdf.query import QueryStore
from rdf.const import *


if __name__ == "__main__":
    server = RedServer(("", 8000))
    server.run_autoload("sample1", "sample1.rdf", "http://redfoot.sourceforge.net/2000/12/sample1/")
    

class UI:

    def __init__(self, location, uri):
        self.rednode = RedNode()
        self.rednode.local.load(location, uri)
        self.editor = Editor(self.rednode)
        
    def handle_request(self, request, response):
        path_info = request.getPathInfo()
        if path_info == "/":
            self.main(response)
        else:
            self.editor.handle_request(request, response)


    def main(self, response):
        response.write("""
        <HTML>
          <HEAD>
            <TITLE>Main Page test</TITLE>
          </HEAD>
          <BODY>
            <H1>Main Page</H1>
            <P>These are the people I know now:</P>
            <UL>
        """)
        for s in self.rednode.get(None, TYPE, "http://redfoot.sourceforge.net/2001/03/Person"):
            response.write("<LI>%s</LI>" % self.rednode.label(s[0]))
        response.write("""
            </UL>
            <P><A HREF="/classList">Go to editor</A>
          </BODY>
        </HTML>
        """)

## $Log$
## Revision 7.1  2001/04/09 17:16:23  eikeon
## storeNode -> rednode
##
## Revision 7.0  2001/03/26 23:41:04  eikeon
## NEW RELEASE
