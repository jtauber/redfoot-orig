from redfoot.viewer import Viewer

class Editor(Viewer):

    def menuBar(self):
        self.writer.write("""
            <P CLASS="MENUBAR"><A HREF=".">Class List</A>
             | <A HREF="subclass">Full Subclass View</A>
             | <A HREF="subclassNR">Collapsed Subclass View</A>
             | <A HREF="RDF">Download RDF</A>
             | <A HREF="Triples">Show Triples</A>
             | EDITOR!!
            </P>
        """)

    def edit(self, subject):
        self.writer.write("""
          <HTML>
            <HEAD>
              <TITLE>ReDFoot: Edit</TITLE>
              <LINK REL="STYLESHEET" HREF="css"/>
            </HEAD>
            <BODY>
              <H1>ReDFoot</H1>""")
        self.menuBar()
        self.writer.write("""
            <H2>%s</H2>
            <P>%s</P>
            <FORM NAME="form" ACTION="edit?uri=%s" METHOD="POST">
              <INPUT NAME="subject" TYPE="HIDDEN" VALUE="%s">
              <TABLE BORDER="1">
        """ % (self.qstore.label(subject), subject, subject, subject))
        self.property_num = 0
        self.qstore.propertyValuesV(subject, self.editProperty)

        self.writer.write("""
              <TR>
                <TD>
                  <SELECT type="text" name="newProperty">

                    <OPTION value="">Select a new Property to add</OPTION>
        """)

        for type in self.qstore.get(subject, self.qstore.TYPE, None):
            for superType in self.qstore.transitiveSuperTypes(type[2]):
                for domain in self.qstore.get(None, self.qstore.DOMAIN, superType):
                    self.writer.write("""
                    <OPTION value="%s">%s</OPTION>
                    """ % (domain[0], self.qstore.label(domain[0])))

        self.writer.write("""
                  </SELECT>

                </TD>

                <TD COLSPAN="2">Click update to be able to specify value</TD>
              </TR>

            </TABLE>

            <INPUT TYPE="HIDDEN" NAME="prop_count" VALUE="%s"/>
            <INPUT TYPE="HIDDEN" NAME="processor"  VALUE="update"/>
            <INPUT TYPE="SUBMIT"                   VALUE="update"/>
          </FORM>

        </BODY>
      </HTML>
      """ % self.property_num)



    def editProperty(self, property, value):
        self.property_num = self.property_num + 1
        self.writer.write("""
                <TR>
                  <TD VALIGN="TOP">%s
                    <INPUT TYPE="HIDDEN" NAME="prop%s_name" VALUE="%s">
                  </TD>
                  <TD VALIGN="TOP">
        """ % (self.qstore.label(property), self.property_num, property))
        for range in self.qstore.get(property, self.qstore.RANGE, None): # TODO: redo as visitor
            self.writer.write("%s<BR>" % range[2])
        self.writer.write("""
                  </TD>
                  <TD>
        """)
        if value[0]=="^":
            self.writer.write("""
                    <INPUT TYPE="TEXT" SIZE="60" NAME="prop%s_value" VALUE="%s">
            """ % (self.property_num, value[1:]))
        else:
            rangelist = self.qstore.get(property, self.qstore.RANGE, None) # already did this above
            if len(rangelist) > 0:
                self.writer.write("""
                    <SELECT NAME="prop%s_value">
                """ % self.property_num)
                for v in self.qstore.getPossibleValues(property):
                    if v==value:
                        self.writer.write("""
                        <OPTION SELECTED="TRUE" VALUE="%s">%s</OPTION>
                        """ % (v, self.qstore.label(v)))
                    else:
                        self.writer.write("""
                        <OPTION VALUE="%s">%s</OPTION>
                        """ % (v, self.qstore.label(v)))
                self.writer.write("""
                    </SELECT>
                """)
            else:
                self.writer.write("""
                    <INPUT TYPE="TEXT" SIZE="60" NAME="prop%s_value" VALUE="%s">***
                """ % (self.property_num, value))
        self.writer.write("""
                </TD>
              </TR>
        """)
