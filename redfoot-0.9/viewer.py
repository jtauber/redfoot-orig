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
          background:  #336699;
          font-weight: normal;
          color:       #FFF;
          padding:     5px 10px;
          margin:      -10px -10px 10px -10px;
        }

        a {
          color:       #000000;
        }

        a:visited {
          color:       #000000;
        }

        a:hover {
          color:       #336699;
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
            <P><A HREF="RDF">Download RDF</A>
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


    def displayClass(self, klass):
        self.writer.write("""
        <DT>%s</DT>
        """ % self.qstore.label(klass))

    def displayResource(self, resource):
        self.writer.write("""
        <DD><A HREF="view?uri=%s" TITLE="%s">%s</A><BR></DD>
        """ % (self.encodeURI(resource),
               self.qstore.comment(resource),
               self.qstore.label(resource)))


    def encodeURI(self, s):
        import string
        return string.join( string.split(s,'#') ,'%23')
