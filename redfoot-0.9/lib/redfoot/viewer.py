# $Header$

from rdf.query import QueryStore
from rdf.literal import literal, un_literal, is_literal
from rdf.const import *

class Viewer:

    def __init__(self, storeNode, path):
        self.storeNode = storeNode
        self.path = path
        self.showNeighbours=0
        
    def handleRequest(self, request, response):
        self.response = response
        
        parameters = request.getParameters()        
        path_info = request.getPathInfo()
        
        if path_info == "/":
            response.setHeader("Content-Type", "text/xml")
            s = parameters['subject']
            if s=="": s=None
            p = parameters['predicate']
            if p=="": p=None
            o = parameters['object']
            if o=="": o=None
            self.RDF(s,p,o)
        elif path_info == "/subclass":
            root = parameters['uri']
            if root=="":
                root = RESOURCE
            self.subclass(root)
        elif path_info == "/subclassNR":
            root = parameters['uri']
            if root=="":
                root = RESOURCE
            self.subclass(root, 0)
        elif path_info == "/classList":
            self.classList()
        elif path_info == "/Triples":
            s = parameters['subject']
            if s=="": s=None
            p = parameters['predicate']
            if p=="": p=None
            o = parameters['object']
            if o=="": o=None
            self.Triples(s,p,o)
        elif path_info == "/css":
            self.css()
        elif path_info == "/view":
            self.view(parameters['uri'])
        elif path_info == "/test":
            self.test(parameters['search'])
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
        self.subclass(RESOURCE, 0)

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
            self.storeNode.resourcesByClassV(self.displayClass, self.displayResource)
        else:
            self.storeNode.local.resourcesByClassV(self.displayClass, self.displayResource)
    
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
	self.storeNode.parentTypesV(root, self.displayParent)
	self.response.write("""
              <DL>
        """)

        if self.showNeighbours==1:
            self.storeNode.subClassV(root, self.displaySCClass, self.displaySCResource, recurse=recurse)
        else:
            self.storeNode.local.subClassV(root, self.displaySCClass, self.displaySCResource, recurse=recurse)
            
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
        """ % (self.storeNode.label(subject), subject))

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

        if self.storeNode.isKnownResource(subject):
            self.storeNode.propertyValuesV(subject, self.displayPropertyValue)
        else:
            self.response.write("<TR><TD>Resource not known of directly</TD></TR>")
        self.storeNode.reifiedV(subject, self.displayReifiedStatements)
        
        self.response.write("""
            </TABLE>
          </BODY>
        </HTML>
        """)

    def displayClass(self, klass):
        self.response.write("""
        <DT>%s</DT>
        """ % self.storeNode.label(klass))

    def displayResource(self, resource):
        self.response.write("""
        <DD>%s<BR></DD>
        """ % self.link(resource))

    def displayParent(self, resource):
        self.response.write("""<A HREF="subclassNR?uri=%s" TITLE="%s">%s</A>"""  % (self.encodeURI(resource), self.storeNode.comment(resource), self.storeNode.label(resource)))

    # TODO: rewrite to use lists
    def displaySCClass(self, klass, depth, recurse):
        self.response.write(3*depth*"&nbsp;")

        if recurse==0:
            self.response.write("""<A HREF="subclassNR?uri=%s" TITLE="%s">""" % (self.encodeURI(klass), self.storeNode.comment(klass)))

        self.response.write("<B>%s</B>" % self.storeNode.label(klass))

        if recurse==0:
            self.response.write("</A>")

        self.response.write("<BR>")

    # TODO: rewrite to use lists
    def displaySCResource(self, resource, depth, recurse):
        self.response.write(3*(depth+1)*"&nbsp;")
        self.response.write(self.link(resource)+"<BR>")

    def link(self, resource):
        return """<A HREF="view?uri=%s" TITLE="%s">%s</A>"""  % (self.encodeURI(resource),
     self.storeNode.comment(resource),
     self.storeNode.label(resource))

    def displayPropertyValue(self, property, value):
        propertyDisplay = self.link(property)
        if len(value)<1:
            valueDisplay = ""
        elif is_literal(value):
            valueDisplay = un_literal(value)
        else:
            valueDisplay = self.link(value)
        self.response.write("""
        <TR><TD>%s</TD><TD></TD><TD COLSPAN="2">%s</TD></TR>
        """ % (propertyDisplay, valueDisplay))

    def displayReifiedStatements(self, subject, predicate, object):
        propertyDisplay = self.link(predicate)
        if len(object)<1:
            valueDisplay = ""
        elif is_literal(object):
            valueDisplay = un_literal(object)
        else:
            valueDisplay = self.link(object)
        self.response.write("""
        <TR CLASS="REIFIED"><TD>%s</TD><TD></TD><TD>%s</TD>
        <TD COLSPAN="3">%s<BR>""" % (propertyDisplay, valueDisplay, self.link(subject)))
        self.storeNode.propertyValuesV(subject, self.displayReifiedStatementPropertyValue)
        self.response.write("""
        </TD></TR>""")

    def displayReifiedStatementPropertyValue(self, property, value):
        if property==TYPE:
            return
        if property==SUBJECT:
            return
        if property==PREDICATE:
            return
        if property==OBJECT:
            return
        propertyDisplay = self.link(property)
        if len(value)<1:
            valueDisplay = ""
        if is_literal(value):
            valueDisplay = un_literal(value)
        else:
            valueDisplay = self.link(value)
        self.response.write("""
        %s: %s<BR>
        """ % (propertyDisplay, valueDisplay))

    def encodeURI(self, s, safe='/'):
        import string
        always_safe = string.letters + string.digits + ' _,.-'
        safe = always_safe + safe
        res = []
        for c in s:
            if c not in safe:
                res.append('%%%02x'%ord(c))
            else:
                if c==' ':
                    res.append('+')
                else:
                    res.append(c)
        return string.joinfields(res, '')

    def RDF(self, subject=None, predicate=None, object=None):
        self.storeNode.local.output(self.response, subject, predicate, object)

    def Triples(self, subject=None, predicate=None, object=None):
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

        def triple(s, p, o, write=self.response.write):            
            write("""
              <TR><TD>%s</TD><TD>%s</TD><TD>%s</TD></TR>
            """ % (s, p, o))
        if self.showNeighbours==1:
            self.storeNode.visit(triple, subject, predicate, object)
        else:
            self.storeNode.local.visit(triple, subject, predicate, object)

        self.response.write("""
            </TABLE>
          </BODY>
        </HTML>
        """)
        

    def test(self, search):
        self.response.write("""
        <HTML>
          <HEAD>
            <TITLE>Test</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>""")
        self.menuBar()
        self.response.write("""
            <H2>Test</H2>
         """)
        subjects = self.storeNode.getSubjects()
        self.response.write("""
            <INPUT TYPE="TEXT" SIZE="60" NAME="a" onChange="document.all.b.value=document.all.a.value">
            <SELECT NAME="b" onChange="document.all.a.value=document.all.b.value">
              <OPTION value="">Select a resource</OPTION>
        """)
        for s in subjects:
            self.response.write("""
              <OPTION VALUE="%s">%s</OPTION>
            """ % (s, self.storeNode.label(s)))
        self.response.write("""
            </SELECT>
            <FORM ACTION="test" METHOD="GET">
              <P>Search for <INPUT NAME="search" TYPE="TEXT" VALUE="%s" SIZE="60"><INPUT TYPE="submit">
            </FORM>
        """ % search)
        if search != "":
            import string
            upper_search = string.upper(search)
            self.response.write("""<UL>""")
            for s in subjects:
                upper_uri = string.upper(s)
                upper_label = string.upper(self.storeNode.label(s))
                upper_comment = string.upper(self.storeNode.comment(s))
                if (string.find(upper_uri,upper_search)!=-1) or \
                   (string.find(upper_label, upper_search)!=-1):
                       self.response.write("""
                         <LI><A HREF="javascript:document.all.a.value='%s'">%s</A></LI>
                       """ % (s, self.storeNode.label(s)))
        self.response.write("""</UL>""")
        self.response.write("""
           </BODY>
        </HTML>
        """)

#~ $Log$
#~ Revision 5.1  2000/12/08 23:02:25  eikeon
#~ encoding fixes
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
#~
#~ Revision 4.11  2000/12/08 08:05:58  eikeon
#~ fixed getByType; fixed references to constants
#~
#~ Revision 4.10  2000/12/08 07:02:43  eikeon
#~ show triple now pays attention to showNeighbours
#~
#~ Revision 4.9  2000/12/07 17:54:04  eikeon
#~ Viewer (and Editor, PeerEditor) no longer have both a qstore and a storeNode
#~
#~ Revision 4.8  2000/12/06 23:26:55  eikeon
#~ Made rednode consistently be the local plus neighbourhood; neighbourhood be only the neighbours; and local be only the local part -- much less confusing
#~
#~ Revision 4.7  2000/12/05 22:43:30  eikeon
#~ moved constants to rdf.const
#~
#~ Revision 4.6  2000/12/05 03:49:07  eikeon
#~ changed all the hardcoded [1:] etc stuff to use un_literal is_literal etc
#~
#~ Revision 4.5  2000/12/04 22:07:35  eikeon
#~ got rid of all the getStore().getStore() stuff by using Multiple inheritance and mixin classes instead of all the classes being wrapper classes
#~
#~ Revision 4.4  2000/12/04 22:00:59  eikeon
#~ got rid of all the getStore().getStore() stuff by using Multiple inheritance and mixin classes instead of all the classes being wrapper classes
#~
#~ Revision 4.3  2000/12/04 01:35:40  eikeon
#~ changed plumbing to new style output method
#~
#~ Revision 4.2  2000/11/23 02:34:07  jtauber
#~ added a test of new UI for picking resources
#~
#~ Revision 4.1  2000/11/20 21:41:31  jtauber
#~ download RDF and view Triples now can take subject,predicate,object parameters
#~
#~ Revision 4.0  2000/11/06 15:57:34  eikeon
#~ VERSION 4.0
#~
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
