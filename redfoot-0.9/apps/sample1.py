# $Header$

from rdf.query import QueryStore
from redfoot.rednode import RedNode
from redfoot.baseUI import BaseUI
from redfoot.editor import PeerEditor

from rdf.const import *


class Sample1UI:

    def __init__(self):
        self.storeNode = RedNode()
        self.storeNode.local.load("sample1.rdf", "http://redfoot.sourceforge.net/2000/12/sample1/")
        self.path = "/2000/12/sample1"
        self.editor = None

    def getEditor(self):
        if self.editor==None:
            self.editor = PeerEditor(self.storeNode, self.path)
        return self.editor

    def path_match(self, path_info):
        return path_info[0:len(self.path)]==self.path

    def call_editor(self, request, response):
        request._pathInfo = request.getPathInfo()[len(self.path):]
        self.getEditor().handleRequest(request, response)

    def handleRequest(self, request, response):
        path_info = request.getPathInfo()

	if path_info[:-1]==self.path:
            self.call_editor(request, response)
        elif self.path_match(path_info):
            if not self.authenticated(request, response):
                return
            self.call_editor(request, response)
        elif path_info=="/":
            self.main(response)
        else:
            self.view(response)

    def main(self, response):
        response.write("""
        <HTML>
          <HEAD>
            <TITLE>Main Page test</TITLE>
          </HEAD>
          <BODY>
            <H1>Main Page</H1>
            <P>These are the people I know about:</P>
            <UL>
        """)
        for s in self.storeNode.get(None, TYPE, "http://redfoot.sourceforge.net/2000/10/#Person"):
            response.write("<LI>%s</LI>" % self.storeNode.label(s[0]))
        response.write("""
            </UL>
            <P><A HREF="%s/classList">Go to editor</A>
          </BODY>
        </HTML>
        """% self.path)

    def view(self, response):
        response.write("""
        <HTML>
          <HEAD>
            <TITLE>Sample1 UI</TITLE>
          </HEAD>
          <BODY>
            <H1>Sample1 UI</H1>
          </BODY>
        </HTML>
        """)


    def authenticated(self, request, response):
        parameters = request.getParameters()
        session = request.getSession()
        if hasattr(session, 'username'):
            return 1
        elif parameters['username']!="" and \
           parameters['password']!="" and parameters['password']=="redfoot":
                session.username = parameters['username']
                return 1
        else:
                response.write("""
<HTML>
  <HEAD>
    <TITLE>Username</TITLE>
  </HEAD>
  <BODY onLoad="document.loginForm.username.focus()">
    <H1>Username</H1>
    <FORM name="loginForm" method="POST">
    <TABLE>
      <TR>
        <TD>Username:</TD>
        <TD><INPUT name="username" type="text"> (Hint: any username will work)</TD>
      </TR>
      <TR>
        <TD>Password:</TD>
        <TD><INPUT name="password" type="password"> (Hint: redfoot)</TD>
      </TR>
      <TR>
        <TD colspan=2"><INPUT value="Login" type="submit"></TD>
      </TR>
    </FORM>
  </BODY>                            
</HTML>
""")
                return 0

        raise "TODO: exception indicating we should never fall though to here"
             

# $Log$
# Revision 1.3  2000/12/07 21:33:25  jtauber
# fixed commandline options and path bugs in sample1
#
# Revision 1.2  2000/12/07 21:21:56  eikeon
# added startup message; fixed type; added focus to username
#
# Revision 1.1  2000/12/07 19:04:20  eikeon
# apps moved here from elsewhere
#
# Revision 4.3  2000/12/05 22:43:30  eikeon
# moved constants to rdf.const
#
# Revision 4.2  2000/12/04 05:21:24  eikeon
# Split server.py into server.py, servlet.py and receiver.py
#
# Revision 4.1  2000/11/07 16:55:33  eikeon
# factored out creation of handler from runServer
#
# Revision 4.0  2000/11/06 15:57:34  eikeon
# VERSION 4.0
#
# Revision 1.7  2000/11/04 03:39:47  eikeon
# changed password input to type password
#
# Revision 1.6  2000/11/04 01:48:43  eikeon
# moved sample authentication from editor.py to sample.py
#
# Revision 1.5  2000/11/03 23:04:08  eikeon
# Added support for cookies and sessions; prefixed a number of methods and variables with _ to indicate they are private; changed a number of methods to mixed case for consistency; added a setHeader method on response -- headers where hardcoded before; replaced writer with response as writer predates and is redundant with repsonse; Added authentication to editor
#
# Revision 1.4  2000/11/02 21:48:27  eikeon
# removed old log messages
#
