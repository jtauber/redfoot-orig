# $Header$

from redfoot.query import QueryStore

class Viewer:

    def __init__(self, writer, storeNode):
        self.writer = writer;
        self.storeNode = storeNode
        self.qstore = QueryStore(storeNode)

    def setWriter(self, writer):
        self.writer = writer

    def css(self):
        self.writer.write("""
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
        self.writer.write("""
            <P CLASS="MENUBAR"><A HREF="classList">Class List</A>
             | <A HREF="subclass">Full Subclass View</A>
             | <A HREF="subclassNR">Collapsed Subclass View</A>
             | <A HREF=".">Download RDF</A>
             | <A HREF="Triples">Show Triples</A>
            </P>
        """)

    def mainPage(self):
        self.subclass(QueryStore.RESOURCE, 0)

    def classList(self):
        self.writer.write("""
        <HTML>
          <HEAD>
            <TITLE>ReDFoot</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>
        """)
        self.menuBar()
        self.writer.write("""
            <DIV CLASS="box">
              <DL>
        """)

        self.storeNode.resourcesByClassV(self.displayClass, self.displayResource)
    
        self.writer.write("""
              </DL>
            </DIV>
          </BODY>
        </HTML>
        """)

    def subclass(self, root, recurse=1):
        self.writer.write("""
        <HTML>
          <HEAD>
            <TITLE>ReDFoot Subclass View</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>""")
        self.menuBar()
        self.writer.write("""
            <DIV CLASS="box">
	""")
	self.qstore.parentTypesV(root, self.displayParent)
	self.writer.write("""
              <DL>
        """)

        self.storeNode.subClassV(root, self.displaySCClass, self.displaySCResource, recurse=recurse)
            
        self.writer.write("""
              </DL>
            </DIV>
          </BODY>
        </HTML>
        """)

    def resourceHeader(self, subject):
        self.writer.write("""
            <H2>%s</H2>
            <P>%s</P>
        """ % (self.qstore.label(subject), subject))

    def view(self, subject):
        self.writer.write("""
        <HTML>
          <HEAD>
            <TITLE>ReDFoot</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>""")
        self.menuBar()
        self.resourceHeader(subject)
        self.writer.write("""
            <H3>View</H3>
            <TABLE>
        """)

        if self.qstore.isKnownResource(subject):
            self.qstore.propertyValuesV(subject, self.displayPropertyValue)
        else:
            self.writer.write("<TR><TD>Resource not known of directly</TD></TR>")
        self.qstore.reifiedV(subject, self.displayReifiedStatements)
        
        self.writer.write("""
            </TABLE>
          </BODY>
        </HTML>
        """)

    def displayClass(self, klass):
        self.writer.write("""
        <DT>%s</DT>
        """ % self.qstore.label(klass))

    def displayResource(self, resource):
        self.writer.write("""
        <DD>%s<BR></DD>
        """ % self.link(resource))

    def displayParent(self, resource):
        self.writer.write("""<A HREF="subclassNR?uri=%s" TITLE="%s">%s</A>"""  % (self.encodeURI(resource), self.qstore.comment(resource), self.qstore.label(resource)))

    # TODO: rewrite to use lists
    def displaySCClass(self, klass, depth, recurse):
        self.writer.write(3*depth*"&nbsp;")

        if recurse==0:
            self.writer.write("""<A HREF="subclassNR?uri=%s" TITLE="%s">""" % (self.encodeURI(klass), self.qstore.comment(klass)))

        self.writer.write("<B>%s</B>" % self.qstore.label(klass))

        if recurse==0:
            self.writer.write("</A>")

        self.writer.write("<BR>")

    # TODO: rewrite to use lists
    def displaySCResource(self, resource, depth, recurse):
        self.writer.write(3*(depth+1)*"&nbsp;")
        self.writer.write(self.link(resource)+"<BR>")

    def link(self, resource):
        return """<A HREF="view?uri=%s" TITLE="%s">%s</A>"""  % (self.encodeURI(resource),
     self.qstore.comment(resource),
     self.qstore.label(resource))

    def displayPropertyValue(self, property, value):
        propertyDisplay = self.link(property)
        if value[0]=="^":
            valueDisplay = value[1:]
        else:
            valueDisplay = self.link(value)
        self.writer.write("""
        <TR><TD>%s</TD><TD></TD><TD COLSPAN="2">%s</TD></TR>
        """ % (propertyDisplay, valueDisplay))

    def displayReifiedStatements(self, subject, predicate, object):
        propertyDisplay = self.link(predicate)
        if object[0]=="^":
            valueDisplay = object[1:]
        else:
            valueDisplay = self.link(object)
        self.writer.write("""
        <TR CLASS="REIFIED"><TD>%s</TD><TD></TD><TD>%s</TD>
        <TD COLSPAN="3">%s<BR>""" % (propertyDisplay, valueDisplay, self.link(subject)))
        self.qstore.propertyValuesV(subject, self.displayReifiedStatementPropertyValue)
        self.writer.write("""
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
        if value[0]=="^":
            valueDisplay = value[1:]
        else:
            valueDisplay = self.link(value)
        self.writer.write("""
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
        #from storeio import StoreIO
        self.storeNode.getStore().output(self.writer)

    def Triples(self):
        self.writer.write("""
        <HTML>
          <HEAD>
            <TITLE>Redfoot Triples</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>""")
        self.menuBar()
        self.writer.write("""
            <H2>Triples</H2>
            <TABLE>
        """)
        for statement in self.qstore.get(None, None, None):
            self.writer.write("""
              <TR><TD>%s</TD><TD>%s</TD><TD>%s</TD></TR>
            """ % (statement[0], statement[1], statement[2]))
        self.writer.write("""
            </TABLE>
          </BODY>
        </HTML>
        """)


# $Log$
# Revision 1.23  2000/10/10 04:29:56  eikeon
# call resourceByClassV and subClassV on storeNode so that we see only what is in the local store for now
#
# Revision 1.22  2000/10/09 22:34:31  jtauber
# RDF is now default view
#
# Revision 1.21  2000/10/09 06:37:24  jtauber
# view and edit now clearly say which they are on screen
#
# Revision 1.20  2000/10/08 23:29:06  jtauber
# collapsed subclass view now includes link(s) to parent(s)
#
# Revision 1.19  2000/10/08 22:40:25  jtauber
# edit/view/reified displays line up better now
#
# Revision 1.18  2000/10/08 06:19:15  eikeon
# Changed default view to be the collapsed subclass view
#
# Revision 1.17  2000/10/07 02:24:46  jtauber
# futzed around a little with fonts and colors; if redfoot doesn't have anything about a queried resource, viewer now says so; reified properties now have a link to the statement
#
# Revision 1.16  2000/10/05 19:32:03  jtauber
# refactored out HTML for resource header
#
# Revision 1.15  2000/10/01 03:58:10  eikeon
# fixed up all the places where I put CVS keywords as keywords in omments... duh
#
# Revision 1.14  2000/10/01 03:07:23  eikeon
# changed viewer to now take a StoreNode; RDF now only outputs the RDF for the StoreNode's store; added Header and Log CVS keywords
#
