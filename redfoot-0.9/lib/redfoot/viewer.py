# $Header$

from rdf.query import QueryStore

class Viewer:

    def __init__(self, storeNode, path):
        self.storeNode = storeNode
        self.path = path
        self.qstore = QueryStore(storeNode)

        self.showNeighbours=0
        
    def handleRequest(self, request, response):
        self.response = response
        
        parameters = request.getParameters()        
        path_info = request.getPathInfo()
        
        if path_info == "/":
            response.setHeader("Content-Type", "text/xml")
            self.RDF()
        elif path_info == "/subclass":
            root = parameters['uri']
            if root=="":
                root = QueryStore.RESOURCE
            self.subclass(root)
        elif path_info == "/subclassNR":
            root = parameters['uri']
            if root=="":
                root = QueryStore.RESOURCE
            self.subclass(root, 0)
        elif path_info == "/classList":
            self.classList()
        elif path_info == "/Triples":
            self.Triples()
        elif path_info == "/css":
            self.css()
        elif path_info == "/view":
            self.view(parameters['uri'])
        else:
            self.response.write("unknown PATH of '%s'" % path_info)

    def css(self):
        self.response.write("""
        body {
          margin:      10px;
        }

        form {
          margin:      0px;
          padding:     0px;
        }

        body, td, th {
          font-family: Verdana;
          font-size:   10pt;
        }

        div.box {
          border: solid 1pt #000;
          padding: 5px 10px;
        }

        h1 {
          font-family: Verdana;
          background:  #990000;
          font-weight: normal;
          color:       #FFF;
          padding:     5px 10px;
          margin:      -10px -10px 10px -10px;
        }

        p.MENUBAR {
          margin: -10px -10px 10px -10px;
          padding: 3px 20px;
          background:  #000000;
          color:       #CCCCCC;
        }

        p.MENUBAR a {
          color:       #CCCCCC;
          text-decoration: none;
        }

        p.MENUBAR a:visited {
          color:       #CCCCCC;
          text-decoration: none;
        }

        p.MENUBAR a:hover {
          color:       #FFFFFF;
          text-decoration: none;
        }

        h2 {
          font-family: Verdana;
          color:       #990000;
          margin:      0px;
        }

        h3 {
          font-family: Verdana;
        }

        a {
          color:       #000000;
        }

        a:visited {
          color:       #000000;
        }

        a:hover {
          color:       #990000;
        }

        dt {
          font-weight: bold;
        }

        table {
          border: solid 1pt #000;
          margin: 5px;
        }

        td {
          background: #CCC;
          margin: 0px;
          padding: 5px;
        }

        tr.REIFIED td {
          border: solid 1pt #990000;
	  background: #FFF;
        }

        p.WARNING {
          color: #C00;
        }

	textarea {
	  font-family: Verdana;
	}
        """)

    def menuBar(self):
        self.response.write("""
            <P CLASS="MENUBAR"><B>VIEW</B>
             : <A HREF="classList">Resources by Class</A>
             | <A HREF="subclass">Full Subclass Tree</A>
             | <A HREF="subclassNR">Partial Subclass Tree</A>
             | <A HREF=".">RDF</A>
             | <A HREF="Triples">Triples</A>
            </P>
        """)

    def mainPage(self):
        self.subclass(QueryStore.RESOURCE, 0)

    def classList(self):
        self.response.write("""
        <HTML>
          <HEAD>
            <TITLE>ReDFoot</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>
        """)
        self.menuBar()
        self.response.write("""
            <DIV CLASS="box">
              <DL>
        """)

        if self.showNeighbours==1:
            self.qstore.resourcesByClassV(self.displayClass, self.displayResource)
        else:
            self.storeNode.resourcesByClassV(self.displayClass, self.displayResource)
    
        self.response.write("""
              </DL>
            </DIV>
          </BODY>
        </HTML>
        """)

    def subclass(self, root, recurse=1):
        self.response.write("""
        <HTML>
          <HEAD>
            <TITLE>ReDFoot Subclass View</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>""")
        self.menuBar()
        self.response.write("""
            <DIV CLASS="box">
	""")
	self.qstore.parentTypesV(root, self.displayParent)
	self.response.write("""
              <DL>
        """)

        if self.showNeighbours==1:
            self.qstore.subClassV(root, self.displaySCClass, self.displaySCResource, recurse=recurse)
        else:
            self.storeNode.subClassV(root, self.displaySCClass, self.displaySCResource, recurse=recurse)
            
        self.response.write("""
              </DL>
            </DIV>
          </BODY>
        </HTML>
        """)

    def resourceHeader(self, subject):
        self.response.write("""
            <H2>%s</H2>
            <P>%s</P>
        """ % (self.qstore.label(subject), subject))

    def view(self, subject):
        self.response.write("""
        <HTML>
          <HEAD>
            <TITLE>ReDFoot</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>""")
        self.menuBar()
        self.resourceHeader(subject)
        self.response.write("""
            <H3>View</H3>
            <TABLE>
        """)

        if self.qstore.isKnownResource(subject):
            self.qstore.propertyValuesV(subject, self.displayPropertyValue)
        else:
            self.response.write("<TR><TD>Resource not known of directly</TD></TR>")
        self.qstore.reifiedV(subject, self.displayReifiedStatements)
        
        self.response.write("""
            </TABLE>
          </BODY>
        </HTML>
        """)

    def displayClass(self, klass):
        self.response.write("""
        <DT>%s</DT>
        """ % self.qstore.label(klass))

    def displayResource(self, resource):
        self.response.write("""
        <DD>%s<BR></DD>
        """ % self.link(resource))

    def displayParent(self, resource):
        self.response.write("""<A HREF="subclassNR?uri=%s" TITLE="%s">%s</A>"""  % (self.encodeURI(resource), self.qstore.comment(resource), self.qstore.label(resource)))

    # TODO: rewrite to use lists
    def displaySCClass(self, klass, depth, recurse):
        self.response.write(3*depth*"&nbsp;")

        if recurse==0:
            self.response.write("""<A HREF="subclassNR?uri=%s" TITLE="%s">""" % (self.encodeURI(klass), self.qstore.comment(klass)))

        self.response.write("<B>%s</B>" % self.qstore.label(klass))

        if recurse==0:
            self.response.write("</A>")

        self.response.write("<BR>")

    # TODO: rewrite to use lists
    def displaySCResource(self, resource, depth, recurse):
        self.response.write(3*(depth+1)*"&nbsp;")
        self.response.write(self.link(resource)+"<BR>")

    def link(self, resource):
        return """<A HREF="view?uri=%s" TITLE="%s">%s</A>"""  % (self.encodeURI(resource),
     self.qstore.comment(resource),
     self.qstore.label(resource))

    def displayPropertyValue(self, property, value):
        propertyDisplay = self.link(property)
        if len(value)<1:
            valueDisplay = ""
        elif value[0]=="^":
            valueDisplay = value[1:]
        else:
            valueDisplay = self.link(value)
        self.response.write("""
        <TR><TD>%s</TD><TD></TD><TD COLSPAN="2">%s</TD></TR>
        """ % (propertyDisplay, valueDisplay))

    def displayReifiedStatements(self, subject, predicate, object):
        propertyDisplay = self.link(predicate)
        if len(object)<1:
            valueDisplay = ""
        elif object[0]=="^":
            valueDisplay = object[1:]
        else:
            valueDisplay = self.link(object)
        self.response.write("""
        <TR CLASS="REIFIED"><TD>%s</TD><TD></TD><TD>%s</TD>
        <TD COLSPAN="3">%s<BR>""" % (propertyDisplay, valueDisplay, self.link(subject)))
        self.qstore.propertyValuesV(subject, self.displayReifiedStatementPropertyValue)
        self.response.write("""
        </TD></TR>""")

    def displayReifiedStatementPropertyValue(self, property, value):
        if property==self.qstore.TYPE:
            return
        if property==self.qstore.SUBJECT:
            return
        if property==self.qstore.PREDICATE:
            return
        if property==self.qstore.OBJECT:
            return
        propertyDisplay = self.link(property)
        if len(value)<1:
            valueDisplay = ""
        if value[0]=="^":
            valueDisplay = value[1:]
        else:
            valueDisplay = self.link(value)
        self.response.write("""
        %s: %s<BR>
        """ % (propertyDisplay, valueDisplay))

    def encodeURI(self, s):
        import string
        # work-around for 2.0b
        import sys
        if sys.version_info[0]==2:
            return string.join(string.split(s,'#'),u'%23')
        else:
            return string.join(string.split(s,'#'),'%23')

    def RDF(self):
        self.storeNode.getStore().output(self.response)

    def Triples(self):
        self.response.write("""
        <HTML>
          <HEAD>
            <TITLE>Redfoot Triples</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>""")
        self.menuBar()
        self.response.write("""
            <H2>Triples</H2>
            <TABLE>
        """)
        for statement in self.qstore.get(None, None, None):
            self.response.write("""
              <TR><TD>%s</TD><TD>%s</TD><TD>%s</TD></TR>
            """ % (statement[0], statement[1], statement[2]))
        self.response.write("""
            </TABLE>
          </BODY>
        </HTML>
        """)


#~ $Log$
#~ Revision 3.3  2000/11/03 23:04:08  eikeon
#~ Added support for cookies and sessions; prefixed a number of methods and variables with _ to indicate they are private; changed a number of methods to mixed case for consistency; added a setHeader method on response -- headers where hardcoded before; replaced writer with response as writer predates and is redundant with repsonse; Added authentication to editor
#~
#~ Revision 3.2  2000/11/02 21:48:27  eikeon
#~ removed old log messages
#~
# Revision 3.1  2000/10/31 05:03:08  eikeon
# mainly Refactored how parameters are accessed (no more [0]'s); some cookie code; a few minor changes regaurding plumbing
#
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
