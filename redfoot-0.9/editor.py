# $Header$

from redfoot.viewer import Viewer

class Editor(Viewer):

    def handler(self, path_info, args):
        if args.has_key("processor"):
            if args["processor"][0] == "update":
                self.update(args)
            elif args["processor"][0] == "create":
                self.create(args)
            elif args["processor"][0] == "save":
                self.save()
            elif args["processor"][0] == "delete":
                self.delete(args)
            elif args["processor"][0][0:4] == "del_":
                self.deleteProperty(args)
            elif args["processor"][0][0:6] == "reify_":
                self.reifyProperty(args)
            elif args["processor"][0] == "connect":
                self.connect(args)
            elif args["processor"][0] == "showNeighbours":
                self.showNeighbours=1
            elif args["processor"][0] == "hideNeighbours":
                self.showNeighbours=0
    
        if path_info == "/edit":
            self.edit(args['uri'][0]) # TODO: check why values of args are lists
	elif path_info == "/add":
            if args.has_key("type"):
                type = args["type"][0]
            else:
                type = None
            self.add(type)
        elif path_info == "/connect":
            self.connectPage()
        else:
            Viewer.handler(self,path_info,args)

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
        if subject[0]=="#":
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

    def editProperty(self, property, value):
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
                </TD>
                <TD VALIGN="TOP">
                  <INPUT TYPE="SUBMIT" NAME="processor" VALUE="del_%s">
                </TD>
		<TD VALIG="TOP">
                  <INPUT TYPE="SUBMIT" NAME="processor" VALUE="reify_%s">
                </TD>
              </TR>
        """ % (self.property_num, self.property_num))

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
        if type == None:
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
        self.writer.write("""
                </TD>
              </TR>
        """)
        self.writer.write("""
          </TABLE>
          <INPUT TYPE="HIDDEN" NAME="processor"  VALUE="create"/>
          <INPUT TYPE="SUBMIT"                   VALUE="create"/>
        """)
        self.writer.write("""
        </FORM>

              <P><A HREF="subclassNR">Return to List (without adding a Resource)</A></P>
            </BODY>
          </HTML>
        """)

    def update(self, params):
        subject = params["uri"][0]
        count = params["prop_count"][0]
        i = 0
	self.qstore.getStore().remove(subject)
        while i < int(count):
            i = i + 1
            property = params["prop%s_name" % i][0]
            if params.has_key("prop%s_value" % i):
                value = params["prop%s_value" % i][0]
            else:
                value = ""
            isLiteral = params["prop%s_isLiteral" % i][0]
            if isLiteral == "yes":
                value = "^" + value
            self.qstore.getStore().add(subject, property, value)
        if params.has_key("newProperty"):
            newProperty = params["newProperty"][0]
            if newProperty!=None and newProperty!="":
                self.qstore.getStore().add(subject, newProperty, "")

    def delete(self, params):
        subject = params["uri"][0]
        self.qstore.getStore().remove(subject, None, None)

    def deleteProperty(self, params):
        property_num = params["processor"][0][4:]
        subject = params["uri"][0]
        property = params["prop%s_name" % property_num][0]
        vName = "prop%s_value" % property_num
        if params.has_key(vName):
            value = params[vName][0]
        else:
            value = ''
        if self.qstore.get(property, self.qstore.RANGE, None)[0][2]==self.qstore.LITERAL:
            value = "^" + value
        self.qstore.getStore().remove(subject, property, value)

    def reifyProperty(self, params):
        property_num = params["processor"][0][6:]
        subject = params["uri"][0]
        property = params["prop%s_name" % property_num][0]
        value = params["prop%s_value" % property_num][0]
        if self.qstore.get(property, self.qstore.RANGE, None)[0][2]==self.qstore.LITERAL:
            value = "^" + value
        self.qstore.reify(self.storeNode.getStore().URI+self.generateURI(), subject, property, value)

    def generateURI(self):
	import time
        return "#T%s" % time.time()

    def create(self, params):
        subject = params["uri"][0]

        if subject[0]=="#":
            subject = self.qstore.getStore().getStore().URI + subject

	self.qstore.getStore().remove(subject)


        # TODO: what to do in the case it already exists?
        self.qstore.getStore().add(subject, self.qstore.LABEL, "^"+params["label"][0])
        self.qstore.getStore().add(subject, self.qstore.TYPE, params["type"][0])

        if params.has_key("prop_count"):
            count = params["prop_count"][0]
            i = 0
            while i < int(count):
                i = i + 1
                property = params["prop%s_name" % i][0]
                value = params["prop%s_value" % i][0]
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

    def connect(self, params):
        if params.has_key("uri"):
            self.qstore.getStore().connectTo(params["uri"][0])


# $Log$
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




