class Viewer:

    def __init__(self, writer, qstore):
        self.writer = writer;
        self.qstore = qstore;

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
          background:  #990000;
          font-weight: normal;
          color:       #FFF;
          padding:     5px 10px;
          margin:      -10px -10px 10px -10px;
        }

        h2 {
          color:       #990000;
          margin:      0px;
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
          background: #FF0;
        }

        p.WARNING {
          color: #C00;
        }
        """)

    def mainPage(self):
        self.writer.write("""
        <HTML>
          <HEAD>
            <TITLE>ReDFoot</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>
            <P><A HREF=".">Class List</A>
             | <A HREF="subclass">Full Subclass View</A>
             | <A HREF="subclassNR">Collapsed Subclass View</A>
             | <A HREF="RDF">Download RDF</A>
             | <A HREF="Triples">Show Triples</A>
            </P>
            <DIV CLASS="box">
              <DL>
        """)

        self.qstore.resourcesByClassV(self.displayClass, self.displayResource)
    
        self.writer.write("""
              </DL>
            </DIV>
          </BODY>
        </HTML>
        """)

    def subclass(self, root):
        self.writer.write("""
        <HTML>
          <HEAD>
            <TITLE>ReDFoot Subclass View</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>
            <P><A HREF=".">Class List</A>
             | <A HREF="subclass">Full Subclass View</A>
             | <A HREF="subclassNR">Collapsed Subclass View</A>
             | <A HREF="RDF">Download RDF</A>
             | <A HREF="Triples">Show Triples</A>
            </P>
            <DIV CLASS="box">
              <DL>
        """)

        self.qstore.subClassV(root, self.displaySCClass, self.displaySCResource)
        self.writer.write("""
              </DL>
            </DIV>
          </BODY>
        </HTML>
        """)

    def subclassNonRecursive(self, root):
        self.writer.write("""
        <HTML>
          <HEAD>
            <TITLE>ReDFoot Subclass View</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>
            <P><A HREF=".">Class List</A>
             | <A HREF="subclass">Full Subclass View</A>
             | <A HREF="subclassNR">Collapsed Subclass View</A>
             | <A HREF="RDF">Download RDF</A>
             | <A HREF="Triples">Show Triples</A>
            </P>
            <DIV CLASS="box">
              <DL>
        """)

        self.qstore.subClassV(root, self.displaySCNRClass, self.displaySCResource, recurse=0)
        self.writer.write("""
              </DL>
            </DIV>
          </BODY>
        </HTML>
        """)

    def view(self, subject):
        self.writer.write("""
        <HTML>
          <HEAD>
            <TITLE>ReDFoot</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>
            <P><A HREF=".">Class List</A>
             | <A HREF="subclass">Full Subclass View</A>
             | <A HREF="subclassNR">Collapsed Subclass View</A>
             | <A HREF="RDF">Download RDF</A>
             | <A HREF="Triples">Show Triples</A>
            </P>
            <H2>%s</H2>
            <TABLE>
        """ % self.qstore.label(subject))

        self.qstore.propertyValuesV(subject, self.displayPropertyValue)

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

    # TODO: rewrite to use lists
    def displaySCClass(self, klass, depth):
        self.writer.write(3*depth*"&nbsp;")
        self.writer.write("<B>%s</B><BR>" % self.qstore.label(klass))

    # TODO: rewrite to use lists
    def displaySCNRClass(self, klass, depth):
        self.writer.write(3*depth*"&nbsp;")
        self.writer.write("""
        <A HREF="subclassNR?uri=%s" TITLE="%s"><B>%s</B></A><BR>
        """ % (self.encodeURI(klass), self.qstore.comment(klass), self.qstore.label(klass)))

    # TODO: rewrite to use lists
    def displaySCResource(self, resource, depth):
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
        <TR><TD>%s</TD><TD>%s</TD></TR>
        """ % (propertyDisplay, valueDisplay))

    def encodeURI(self, s):
        import string
        return string.join( string.split(s,'#') ,'%23')

    def RDF(self):
        self.writer.write("RDF")

    def Triples(self):
        self.writer.write("""
        <HTML>
          <HEAD>
            <TITLE>Redfoot Triples</TITLE>
            <LINK REL="STYLESHEET" HREF="css"/>
          </HEAD>
          <BODY>
            <H1>ReDFoot</H1>
            <P><A HREF=".">Class List</A>
             | <A HREF="subclass">Full Subclass View</A>
             | <A HREF="subclassNR">Collapsed Subclass View</A>
             | <A HREF="RDF">Download RDF</A>
             | <A HREF="Triples">Show Triples</A>
            </P>
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
