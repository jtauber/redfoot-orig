# $Header$

from rdf.query import QueryStore
from rdf.literal import literal, un_literal, is_literal
from rdf.const import *

class Viewer:

    def __init__(self, storeNode, path):
        self.storeNode = storeNode
        self.path = path
        self.showNeighbours = 0
        
    def handle_request(self, request, response):
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
            self.rdf(s,p,o)
        elif path_info == "/fullsubclass":
            root = parameters['uri']
            if root=="":
                root = RESOURCE
            self.subclass(root)
        elif path_info == "/subclass":
            root = parameters['uri']
            if root=="":
                root = RESOURCE
            self.subclass(root, 0)
        elif path_info == "/classList":
            self.classList()
        elif path_info == "/triples":
            s = parameters['subject']
            if s=="": s=None
            p = parameters['predicate']
            if p=="": p=None
            o = parameters['object']
            if o=="": o=None
            self.triples(s,p,o)
        elif path_info == "/css":
            self.css()
        elif path_info == "/view":
            self.view(parameters['uri'])
        elif path_info == "/test":
            self.test(parameters['search'])
        elif path_info == "/graphViz":
            self.graphViz()
        else:
            self.response.write("unknown PATH of '%s'" % path_info)

    def getNodeInScope(self):
        if self.showNeighbours==1:
            return self.storeNode.neighbourhood
        else:
            return self.storeNode

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
          font-weight: normal;
          color:       #990000;
          margin:      0px;
        }

        h3 {
          font-family: Verdana;
          font-weight: normal;
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
             | <A HREF="fullsubclass">Full Subclass Tree</A>
             | <A HREF="subclass">Partial Subclass Tree</A>
             | <A HREF=".">RDF</A>
             | <A HREF="triples">Triples</A>
            </P>
        """)

    def mainPage(self):
        self.subclass(RESOURCE, 0)

    def header(self, title):
        self.response.write("""
            <HTML>
              <HEAD>
                <TITLE>ReDFoot: %s</TITLE>
                <LINK REL="STYLESHEET" HREF="css"/>
              </HEAD>
              <BODY>
                <H1>RedFoot</H1>
        """ % title)
        self.menuBar()
        self.response.write("""
                <H2>%s</H2>
        """ % title)

    def footer(self):
        self.response.write("""
              </BODY>
            </HTML>
        """)

    def classList(self):
        self.header("Resources by Class")
        self.response.write("""
            <DIV CLASS="box">
              <DL>
        """)

        node = self.getNodeInScope()
        node.visitResourcesByType(self.displayClass, self.displayResource)
        
        firstTypeless = 1

        for resource in node.getTypelessResources():
            if firstTypeless==1:
                self.response.write("""<DT>Typeless</DT>""")
                firstTypeless=0
            self.displayResource(resource)
        
        self.response.write("""
              </DL>
            </DIV>
        """)
        self.footer()

    def subclass(self, root, recurse=1):
        self.header("Subclass View")
        self.response.write("""
            <DIV CLASS="box">
	""")
	self.storeNode.visitParentTypes(self.displayParent, root)
	self.response.write("""
              <DL>
        """)

        node = self.getNodeInScope()
        node.visitSubclasses(self.displaySCClass, self.displaySCResource, root, recurse=recurse)
            
        self.response.write("""
              </DL>
            </DIV>
        """)
        self.footer()

    def resourceHeader(self, subject):
        self.response.write("""
            <H3>%s</H3>
            <P>%s</P>
        """ % (self.encodeCharacterData(self.storeNode.label(subject)), subject))

    def view(self, subject):
        self.header("View")
        self.resourceHeader(subject)
        self.response.write("""
            <TABLE>
        """)

        if self.storeNode.isKnownResource(subject):
            self.storeNode.visitPredicateObjectPairsForSubject(self.displayPropertyValue, subject)
        else:
            self.response.write("<TR><TD>Resource not known of directly</TD></TR>")
        self.storeNode.visitReifiedStatementsAboutSubject(self.displayReifiedStatements, subject)
        
        self.response.write("""
            </TABLE>
        """)
        self.footer()

    def displayClass(self, klass):
        self.response.write("""
        <DT>%s</DT>
        """ % self.encodeCharacterData(self.storeNode.label(klass)))

    def displayResource(self, resource):
        self.response.write("""
        <DD>%s<BR></DD>
        """ % self.link(resource))

    def displayParent(self, resource):
        self.response.write("""<A HREF="subclass?uri=%s" TITLE="%s">%s</A>"""  % (self.encodeURI(resource), self.encodeAttributeValue(self.storeNode.comment(resource)), self.encodeCharacterData(self.storeNode.label(resource))))

    # TODO: rewrite to use lists
    def displaySCClass(self, klass, depth, recurse):
        self.response.write(3*depth*"&nbsp;")

        if recurse==0:
            self.response.write("""<A HREF="subclass?uri=%s" TITLE="%s">""" % (self.encodeURI(klass), self.encodeAttributeValue(self.storeNode.comment(klass))))

        self.response.write("<B>%s</B>" % self.encodeCharacterData(self.storeNode.label(klass)))

        if recurse==0:
            self.response.write("</A>")

        self.response.write("<BR>")

    # TODO: rewrite to use lists
    def displaySCResource(self, resource, depth, recurse):
        self.response.write(3*(depth+1)*"&nbsp;")
        self.response.write(self.link(resource)+"<BR>")

    def link(self, resource):
        return """<A HREF="view?uri=%s" TITLE="%s">%s</A>"""  % (self.encodeURI(resource),
                                                                 self.encodeAttributeValue(self.storeNode.comment(resource)),
                                                                 self.encodeCharacterData(self.storeNode.label(resource)))

    def displayPropertyValue(self, property, value):
        propertyDisplay = self.link(property)
        if len(value)<1:
            valueDisplay = ""
        elif is_literal(value):
            valueDisplay = self.encodeCharacterData(un_literal(value))
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
            valueDisplay = self.encodeCharacterData(un_literal(object))
        else:
            valueDisplay = self.link(object)
        self.response.write("""
        <TR CLASS="REIFIED"><TD>%s</TD><TD></TD><TD>%s</TD>
        <TD COLSPAN="3">%s<BR>""" % (propertyDisplay, valueDisplay, self.link(subject)))
        self.storeNode.visitPredicateObjectPairsForSubject(self.displayReifiedStatementPropertyValue, subject)
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
            valueDisplay = self.encodeCharacterData(un_literal(value))
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

    def encodeAttributeValue(self, s):
        import string
        s = string.join(string.split(s, '&'), '&amp;')
        s = string.join(string.split(s, '"'), '&quot;')
        return s

    def encodeCharacterData(self, s):
        import string
        s = string.join(string.split(s, '&'), '&amp;')
        s = string.join(string.split(s, '<'), '&lt;')
        return s

    def rdf(self, subject=None, predicate=None, object=None):
        node = self.getNodeInScope()
        node.output(self.response, None, subject, predicate, object)

    def triples(self, subject=None, predicate=None, object=None):
        self.header("Triples")
        self.response.write("""
            <TABLE>
        """)

        def triple(s, p, o, write=self.response.write):            
            write("""
              <TR><TD>%s</TD><TD>%s</TD><TD>%s</TD></TR>
            """ % (s, p, o))
        if self.showNeighbours==1:
            self.storeNode.neighbourhood.visit(triple, subject, predicate, object)
        else:
            self.storeNode.local.visit(triple, subject, predicate, object)

        self.response.write("""
            </TABLE>
        """)
        self.footer()

    def test(self, search):
        self.header("Test")
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
        self.footer()

    def graphViz(self):
        self.response.write("""
            digraph G {
        """)
        def callback(s,p,o,response=self.response, node=self.storeNode):
            response.write("""
	        "%s" -> "%s" [ label="%s" ];
            """ % (node.label(s), node.label(o), node.label(p)))
        self.getNodeInScope().visit(callback, None, None, None)
        self.response.write("""
            }
        """)

#~ $Log$
#~ Revision 5.18  2001/02/07 17:27:44  eikeon
#~ bug fix... query parameters to output were not being passed correctly
#~
#~ Revision 5.17  2000/12/20 21:22:08  eikeon
#~ converted many mixedCase names to _ style names
#~
#~ Revision 5.16  2000/12/20 04:04:39  jtauber
#~ fixed typo in encodeAttributeValue name
#~
#~ Revision 5.15  2000/12/20 03:14:48  jtauber
#~ added encoding of special chars in attribute values and character data
#~
#~ Revision 5.14  2000/12/19 06:04:04  eikeon
#~ Moved the 'local in context of neighbourhood' methods to RedNode... else we where overriding the corresponding methods on local, which someone may care about
#~
#~ Revision 5.13  2000/12/17 23:41:58  eikeon
#~ removed of log messages
#~
#~ Revision 5.12  2000/12/13 02:54:11  jtauber
#~ moved functions in query around and renamed a lot
#~
#~ Revision 5.11  2000/12/10 01:19:13  jtauber
#~ init attempt at generating dot for graphviz
#~
#~ Revision 5.10  2000/12/09 23:02:12  jtauber
#~ fixed font-weight and size
#~
#~ Revision 5.9  2000/12/09 22:56:40  jtauber
#~ removed second menubar in view
#~
#~ Revision 5.8  2000/12/09 22:52:49  eikeon
#~ factored out the if self.showNeighbours
#~
#~ Revision 5.7  2000/12/09 22:33:59  jtauber
#~ factored out header/footer
#~
#~ Revision 5.6  2000/12/09 22:20:25  jtauber
#~ fullsubclass method is now subclass :-)
#~
#~ Revision 5.5  2000/12/09 22:16:00  jtauber
#~ RDF -> rdf; Triples -> triple
#~
#~ Revision 5.4  2000/12/09 22:05:04  jtauber
#~ subclass -> fullsubclass; subclassNR -> subclass
#~
#~ Revision 5.3  2000/12/09 18:37:52  jtauber
#~ class list now lists typeless resources
#~
#~ Revision 5.2  2000/12/09 00:44:59  eikeon
#~ improved encodeURI function
#~
#~ Revision 5.1  2000/12/08 23:02:25  eikeon
#~ encoding fixes
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
