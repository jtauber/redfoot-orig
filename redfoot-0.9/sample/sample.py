# $Header$

from rdf.query import QueryStore
from redfoot.baseUI import BaseUI

class SampleUI(BaseUI):

    def handleRequest(self, request, response):
        path_info = request.getPathInfo()

        if self.path_match(path_info):
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
            <TITLE>Main Page</TITLE>
          </HEAD>
          <BODY>
            <H1>Main Page</H1>
            <P>These are the people I know about:</P>
            <UL>
        """)
        for s in self.qstore.get(None, QueryStore.TYPE, "http://redfoot.sourceforge.net/2000/10/#Person"):
            response.write("<LI>%s</LI>" % self.qstore.label(s[0]))
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
            <TITLE>Sample UI</TITLE>
          </HEAD>
          <BODY>
            <H1>Sample UI</H1>
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
  <H1>Username</H1>
  <FORM method="POST">
  <TABLE>
    <TR>
      <TD>Username:</TD>
      <TD><INPUT name="username" type="text"> (Hint: any username will work)</TD>
    </TR>
    <TR>
      <TD>Password:</TD>
      <TD><INPUT name="password" type="password"> (Hint: refoot)</TD>
      </TD>
    </TR>
    <TR>
      <TD colspan=2"><INPUT value="Login" type="submit"></TD>
    </TR>
  </FORM>
</HTML>
""")
                return 0

        raise "TODO: exception indicating we should never fall though to here"
            
if __name__ == '__main__':
    import sys
    from redfoot.server import RedServer
    redfoot = RedServer()
    redfoot.runServer(sys.argv[1:])

    handler = SampleUI(redfoot.storeNode, redfoot.path)
    redfoot.server.setHandler(handler)
    redfoot.server.start()
    
    redfoot.keepRunning()

# $Log$
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
