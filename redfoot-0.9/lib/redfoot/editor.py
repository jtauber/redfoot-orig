# $Header$

from redfoot.viewer import Viewer

class Editor(Viewer):

    def handleRequest(self, request, response):
        parameters = request.getParameters()
        path_info = request.path_info

        processor = parameters['processor']
        if processor == "update":
            self.update(parameters)
        elif processor == "create":
            self.create(parameters)
        elif processor == "save":
            self.save()
        elif processor == "delete":
            self.delete(parameters)
        elif processor[0:4] == "del_":
            self.deleteProperty(parameters)
        elif processor[0:6] == "reify_":
            self.reifyProperty(parameters)
        elif processor == "connect":
            self.connect(parameters)
        elif processor == "showNeighbours":
            self.showNeighbours=1
        elif processor == "hideNeighbours":
            self.showNeighbours=0
    
        if path_info == "/edit":
            self.edit(parameters['uri']) 
	elif path_info == "/add":
            self.add(parameters['type'])
        elif path_info == "/connect":
            self.connectPage()
        else:
            request.path_info = path_info
            Viewer.handleRequest(self, request, response)

    def menuBar(self):
        Viewer.menuBar(self)
        self.writer.write("""
            <P CLASS="MENUBAR"><B>EDIT</B>
             : <A HREF="add">Add a Resource</A>
             | <A HREF="?processor=save">Save Node to Disk</A>
            </P>
        """)

    def resourceHeader(self, subject):
        self.writer.write("""
            <H2>%s</H2>
            <P>%s - <A HREF="view?uri=%s">view</A>|<A HREF="edit?uri=%s">edit</A>
        """ % (self.qstore.label(subject), subject, self.encodeURI(subject), self.encodeURI(subject)))

    def edit(self, subject):
        if subject!=None and subject!="" and subject[0]=="#":
            subject = self.qstore.getStore().getStore().URI + subject

        self.writer.write("""
          <HTML>
            <HEAD>
              <TITLE>ReDFoot: Edit</TITLE>
              <LINK REL="STYLESHEET" HREF="css"/>
            </HEAD>
            <BODY>
              <H1>ReDFoot</H1>""")
        self.menuBar()
        self.resourceHeader(subject)
        self.writer.write("""
            <H3>Edit</H3>
            <FORM NAME="form" ACTION="edit?uri=%s" METHOD="POST">
              <INPUT NAME="uri" TYPE="HIDDEN" VALUE="%s">
              <TABLE>
        """ % (subject, subject))
        self.property_num = 0

        if self.qstore.isKnownResource(subject):
            # self.qstore.propertyValuesV(subject, self.editProperty)
            self.qstore.propertyValuesLocalV(subject, self.editProperty)
            self.qstore.propertyValuesNeighbourhoodV(subject, self.displayPropertyValue)
        
	    self.qstore.reifiedV(subject, self.displayReifiedStatements)

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

                <TD COLSPAN="5">Click update to be able to specify value</TD>
              </TR>

            </TABLE>

            <INPUT TYPE="HIDDEN" NAME="prop_count" VALUE="%s"/>
            <INPUT TYPE="SUBMIT" NAME="processor"  VALUE="update"/>
            <INPUT TYPE="SUBMIT" NAME="processor"  VALUE="delete"/>
          </FORM>
              """ % self.property_num)
        else:
            self.writer.write("<TR><TD>Resource not known of directly</TD></TR></TABLE></FORM>")

        self.writer.write("""
        </BODY>
      </HTML>
      """)

    UITYPE = "http://redfoot.sourceforge.net/2000/10/06/builtin#uiType"
    TEXTAREA = "http://redfoot.sourceforge.net/2000/10/06/builtin#TEXTAREA"
    REQUIREDPROPERTY = "http://redfoot.sourceforge.net/2000/10/06/builtin#requiredProperty"    

    def editProperty(self, property, value, exists=1):
        self.property_num = self.property_num + 1
        self.writer.write("""
                <TR>
                  <TD VALIGN="TOP">%s
                    <INPUT TYPE="HIDDEN" NAME="prop%s_name" VALUE="%s">
                  </TD>
                  <TD VALIGN="TOP">
        """ % (self.qstore.label(property), self.property_num, property))

        def callback(s, p, o, self=self):
            self.writer.write("%s<BR>" % self.qstore.label(o))
        self.qstore.visit(callback, property, self.qstore.RANGE, None)

        self.writer.write("""
                  </TD>
                  <TD COLSPAN="2">
        """)
        if (len(value) > 0 and value[0]=="^") or (len(value)==0 and self.qstore.get(property, self.qstore.RANGE, None)[0][2]==self.qstore.LITERAL):
            uitype = self.qstore.get(property, self.UITYPE, None)
            if len(uitype) > 0 and uitype[0][2]==self.TEXTAREA:
                self.writer.write("""
                <TEXTAREA NAME="prop%s_value" ROWS="5" COLS="60">%s</TEXTAREA>
                """ % (self.property_num, value[1:]))
            else:
                self.writer.write("""
                <INPUT TYPE="TEXT" SIZE="60" NAME="prop%s_value" VALUE="%s">
                """ % (self.property_num, value[1:]))
            self.writer.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_isLiteral" VALUE="yes">
            """ % self.property_num)
        else:
            rangelist = self.qstore.get(property, self.qstore.RANGE, None) # already did this above
            if len(rangelist) > 0:
                self.writer.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_isLiteral" VALUE="no">
                    <SELECT NAME="prop%s_value">
                      <OPTION value="">Select a value for this property</OPTION>
                """ % (self.property_num, self.property_num))
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
                </TD>""")
        if exists:
            self.writer.write("""
                <TD VALIGN="TOP">
                  <INPUT TYPE="SUBMIT" NAME="processor" VALUE="del_%s">
                </TD>
		<TD VALIG="TOP">
                  <INPUT TYPE="SUBMIT" NAME="processor" VALUE="reify_%s">
                </TD>"""  % (self.property_num, self.property_num))
        self.writer.write("""
              </TR>
        """)

    def add(self, type):
        self.writer.write("""
          <HTML>
            <HEAD>
              <TITLE>ReDFoot: Add</TITLE>
              <LINK REL="stylesheet" HREF="css"/>
            </HEAD>
            <BODY>
              <H1>ReDFoot</H1>""")
        self.menuBar()
        self.writer.write("""
          <FORM NAME="form" ACTION="edit" METHOD="POST">
            <TABLE>
              <TR>
                <TD VALIGN="TOP">URI</TD>
                <TD>&nbsp;</TD>
                <TD>
                  <INPUT TYPE="TEXT" SIZE="60" NAME="uri" value="%s"/>
                </TD>
              </TR>""" % (self.generateURI()))
        self.writer.write("""
              <TR>
                <TD VALIGN="TOP">label</TD>
                <TD>Literal</TD>
                <TD>
                  <INPUT TYPE="TEXT" SIZE="60" NAME="label" />
                </TD>
              </TR>

              <TR>
                <TD VALIGN="TOP">type</TD>
                <TD>Class</TD>
                <TD>""")

        self.property_num = 0
        if type == "":
            self.writer.write("""
                  <SELECT SIZE="1" NAME="type">
            """)
            for klass in self.qstore.get(None, self.qstore.TYPE, self.qstore.CLASS):
                self.writer.write("""
                    <OPTION VALUE="%s">%s</OPTION>
                """ % (klass[0], self.qstore.label(klass[0])))
            self.writer.write("""
                  </SELECT>
            """)
        else:
            self.writer.write("""
                  <INPUT TYPE="HIDDEN" NAME="type" VALUE="%s"/>
                  %s
            """ % (type, self.link(type)))

            # TODO: make this a func... getProperties for subject?
            for superType in self.qstore.transitiveSuperTypes(type):
                for domain in self.qstore.get(None, self.qstore.DOMAIN, superType):
                    property = domain[0]
                    if len(self.qstore.get(property, self.REQUIREDPROPERTY, "http://redfoot.sourceforge.net/2000/10/06/builtin#YES"))>0:
                        self.editProperty(property, "", 0)
            
        self.writer.write("""
                </TD>
              </TR>
        """)
        self.writer.write("""
          </TABLE>
            <INPUT TYPE="HIDDEN" NAME="prop_count" VALUE="%s"/>
            <INPUT TYPE="HIDDEN" NAME="processor"  VALUE="create"/>
          <INPUT TYPE="SUBMIT"                   VALUE="create"/>
        """ % self.property_num)
        self.writer.write("""
        </FORM>

              <P><A HREF="subclassNR">Return to List (without adding a Resource)</A></P>
            </BODY>
          </HTML>
        """)

    def update(self, parameters):
        subject = parameters['uri']
        count = parameters['prop_count']
        i = 0
	self.qstore.getStore().remove(subject)
        while i < int(count):
            i = i + 1
            property = parameters['prop%s_name' % i]
            value = parameters['prop%s_value' % i]
            isLiteral = parameters['prop%s_isLiteral' % i]
            if isLiteral == "yes":
                value = "^" + value
            self.qstore.getStore().add(subject, property, value)
        newProperty = parameters['newProperty']
        if newProperty!="":
            self.qstore.getStore().add(subject, newProperty, "")

    def delete(self, parameters):
        subject = parameters['uri']
        if subject=="":
            raise "TODO: invalid subject"
        self.qstore.getStore().remove(subject, None, None)

    def deleteProperty(self, parameters):
        property_num = parameters['processor'][4:]
        subject = parameters['uri']
        property = parameters['prop%s_name' % property_num]
        vName = "prop%s_value" % property_num
        value = parameters[vName]
        if self.qstore.get(property, self.qstore.RANGE, None)[0][2]==self.qstore.LITERAL:
            value = "^" + value
        self.qstore.getStore().remove(subject, property, value)

    def reifyProperty(self, parameters):
        property_num = parameters['processor'][6:]
        subject = parameters['uri']
        property = parameters['prop%s_name' % property_num]
        value = parameters['prop%s_value' % property_num]
        if self.qstore.get(property, self.qstore.RANGE, None)[0][2]==self.qstore.LITERAL:
            value = "^" + value
        self.qstore.reify(self.storeNode.getStore().URI+self.generateURI(), subject, property, value)

    def generateURI(self):
	import time
        return "#T%s" % time.time()

    def create(self, parameters):
        subject = parameters['uri']

        if subject[0]=="#":
            subject = self.qstore.getStore().getStore().URI + subject

	self.qstore.getStore().remove(subject)


        # TODO: what to do in the case it already exists?
        self.qstore.getStore().add(subject, self.qstore.LABEL, "^"+parameters['label'])
        self.qstore.getStore().add(subject, self.qstore.TYPE, parameters['type'])

        count = parameters["prop_count"]
        if count=="":
            count=0
        else:
            count = int(count)
        
        i = 0
        while i < count:
            i = i + 1
            property = parameters['prop%s_name' % i]
            valueName = "prop%s_value" % i
            value = parameters[valueName]
            isLiteral = parameters['prop%s_isLiteral' % i]
            if isLiteral == "yes":
                value = "^" + value
            self.qstore.getStore().add(subject, property, value)

    def save(self):
        self.qstore.getStore().getStore().save()


#TODO: could be a separate module
class PeerEditor(Editor):

    def menuBar(self):
        Editor.menuBar(self)
        self.writer.write("""
            <P CLASS="MENUBAR"><B>PEER</B>
             : <A HREF="connect">Connect Neighbour</A>
             |""")

        if self.showNeighbours==1:
            self.writer.write("""
            <A HREF="?processor=hideNeighbours">Hide Neighbour Resources</A>""")
        else:
            self.writer.write("""
            <A HREF="?processor=showNeighbours">Show Neighbour Resources</A>""")

        self.writer.write("""
            </P>
        """)
    
    def connectPage(self):
        self.writer.write("""
          <HTML>
            <HEAD>
              <TITLE>ReDFoot: Connect</TITLE>
              <LINK REL="STYLESHEET" HREF="css"/>
            </HEAD>
            <BODY>
              <H1>ReDFoot</H1>""")
        self.menuBar()
        self.writer.write("""
              <H2>Connect Neighbour</H2>
        
              <FORM NAME="form" ACTION="subclassNR" METHOD="POST">
                <P>URI to Connect: <INPUT TYPE="TEXT" NAME="uri" SIZE="60">
                <INPUT TYPE="SUBMIT" NAME="processor"  VALUE="connect"/>
                </P>
              </FORM>
            </BODY>
          </HTML>
          """)

    def connect(self, parameters):
        uri = parameters["uri"]
        if uri!="":
            self.qstore.getStore().connectTo(uri)


# $Log$
# Revision 3.2  2000/10/31 05:03:08  eikeon
# mainly Refactored how parameters are accessed (no more [0]'s); some cookie code; a few minor changes regaurding plumbing
#
# Revision 3.1  2000/10/29 01:54:35  eikeon
# fixed Unknown Attribute property_num bug I introduced just before 0.9.1 ;(
#
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
#
# Revision 1.2  2000/10/26 19:41:54  eikeon
# finished suppport for add(type)
#
# Revision 1.1  2000/10/25 20:40:31  eikeon
# changes relating to new directory structure
#
# Revision 2.6  2000/10/16 18:49:05  eikeon
# converted a number of store.get()s to store.visit()s
#
# Revision 2.5  2000/10/16 05:27:17  jtauber
# gave menu bars labels and clarified some of the items
#
# Revision 2.4  2000/10/16 05:02:28  jtauber
# refactored menu bar to remove duplication between different UIs
#
# Revision 2.3  2000/10/16 04:49:57  jtauber
# fixed bug where Editor's handler was incorrectly calling the handler on its superclass Viewer
#
# Revision 2.2  2000/10/16 04:10:07  jtauber
# refactored editor-specific http handling code from viewer to editor
#
# Revision 2.1  2000/10/16 04:01:23  jtauber
# (finally) added $ and $ to Editor
#




