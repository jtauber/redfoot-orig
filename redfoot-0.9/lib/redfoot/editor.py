# $Header$

from redfoot.viewer import Viewer
from rdf.literal import literal, un_literal, is_literal

from rdf.const import *

class Editor(Viewer):

    def handle_request(self, request, response):
        self.response = response
        self.request = request
        
        parameters = request.getParameters()
        path_info = request.getPathInfo()

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
            request.setPathInfo(path_info)
            Viewer.handle_request(self, request, response)

    def menuBar(self):
        Viewer.menuBar(self)
        self.response.write("""
            <P CLASS="MENUBAR"><B>EDIT</B>
             : <A HREF="add">Add a Resource</A>
             | <A HREF="?processor=save">Save Node to Disk</A>
            </P>
        """)

    def resourceHeader(self, subject):
        self.response.write("""
            <H3>%s</H3>
            <P>%s - <A HREF="view?uri=%s">view</A>|<A HREF="edit?uri=%s">edit</A>
        """ % (self.encodeCharacterData(self.storeNode.label(subject)), subject, self.encodeURI(subject), self.encodeURI(subject)))

    def edit(self, subject):
        if subject!=None and subject!="" and subject[0]=="#":
            subject = self.storeNode.local.URI + subject

        self.header("Edit")
        self.resourceHeader(subject)
        self.response.write("""
            <FORM NAME="form" ACTION="edit?uri=%s" METHOD="POST">
              <INPUT NAME="uri" TYPE="HIDDEN" VALUE="%s">
              <TABLE>
        """ % (subject, subject))
        self.property_num = 0

        if self.storeNode.isKnownResource(subject):
            self.storeNode.local.visitPredicateObjectPairsForSubject(self.editProperty, subject)
            self.storeNode.neighbours.visitPredicateObjectPairsForSubject(self.displayPropertyValue, subject)
        
	    self.storeNode.visitReifiedStatementsAboutSubject(self.displayReifiedStatements, subject)

            self.response.write("""
              <TR>
                <TD>
                  <SELECT type="text" name="newProperty">

                    <OPTION value="">Select a new Property to add</OPTION>
            """)

            def possibleProperty(s, p, o, self=self):
                self.response.write("""
                    <OPTION value="%s">%s</OPTION>
                                    """ % (s, self.storeNode.label(s)))
            self.storeNode.visitPossiblePropertiesForSubject(possibleProperty, subject)


            def option(s, p, o, write=self.response.write, neighbourhood=self.storeNode.neighbourhood):
                write("""
                        <OPTION value="%s">%s</OPTION>
                      """ % (p, neighbourhood.label(p)))

            # call to non existant visitor version goes here
    
                        
            self.response.write("""
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
            self.response.write("<TR><TD>Resource not known of directly</TD></TR></TABLE></FORM>")

        self.footer()

    UITYPE = "http://redfoot.sourceforge.net/2000/10/06/builtin#uiType"
    TEXTAREA = "http://redfoot.sourceforge.net/2000/10/06/builtin#TEXTAREA"
    REQUIREDPROPERTY = "http://redfoot.sourceforge.net/2000/10/06/builtin#requiredProperty"    

    def editProperty(self, property, value, exists=1):
        self.property_num = self.property_num + 1
        self.response.write("""
                <TR>
                  <TD VALIGN="TOP">%s
                    <INPUT TYPE="HIDDEN" NAME="prop%s_name" VALUE="%s">
                  </TD>
                  <TD VALIGN="TOP">
        """ % (self.storeNode.label(property), self.property_num, property))

        def callback(s, p, o, self=self):
            self.response.write("%s<BR>" % self.storeNode.label(o))
        self.storeNode.visit(callback, property, RANGE, None)

        self.response.write("""
                  </TD>
                  <TD COLSPAN="2">
        """)
        if (len(value) > 0 and is_literal(value[0])) or (len(value)==0 and self.storeNode.getRange(property)==LITERAL):
            uitype = self.storeNode.getFirst(property, self.UITYPE, None)
            if uitype != None and uitype[2]==self.TEXTAREA:
                self.response.write("""
                <TEXTAREA NAME="prop%s_value" ROWS="5" COLS="60">%s</TEXTAREA>
                """ % (self.property_num, un_literal(value)))
            else:
                self.response.write("""
                <INPUT TYPE="TEXT" SIZE="60" NAME="prop%s_value" VALUE="%s">
                """ % (self.property_num, self.encodeAttributeValue(un_literal(value))))
            self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_isLiteral" VALUE="yes">
            """ % self.property_num)
        else:
            rangelist = self.storeNode.get(property, RANGE, None) # already did this above
            if len(rangelist) > 0:
                self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_isLiteral" VALUE="no">
                    <SELECT NAME="prop%s_value">
                      <OPTION value="">Select a value for this property</OPTION>
                """ % (self.property_num, self.property_num))


                possibleValues = {}
                def possibleValue(s, p, o, storeNode=self.storeNode, possibleValues=possibleValues):
                    label = storeNode.label(s)
                    # we use a key of 'label + s' to insure uniqness of key
                    possibleValues[label+s] = s 

                self.storeNode.visitPossibleValues(possibleValue, property)

                pvs = possibleValues.keys()
                pvs.sort()

                for pv in pvs:
                    v = possibleValues[pv]
                    if v==value:
                        self.response.write("""
                        <OPTION SELECTED="TRUE" VALUE="%s">%s</OPTION>
                        """ % (v, self.storeNode.label(v)))
                    else:
                        self.response.write("""
                        <OPTION VALUE="%s">%s</OPTION>
                        """ % (v, self.storeNode.label(v)))
                    


                self.response.write("""
                    </SELECT>
                """)
            else:
                #TODO 
                self.response.write("""
                    <INPUT TYPE="TEXT" SIZE="60" NAME="prop%s_value" VALUE="%s">***
                """ % (self.property_num, encodeAttributeValue(value)))
        self.response.write("""
                </TD>""")
        if exists:
            self.response.write("""
                <TD VALIGN="TOP">
                  <INPUT TYPE="SUBMIT" NAME="processor" VALUE="del_%s">
                </TD>
		<TD VALIGN="TOP">
                  <INPUT TYPE="SUBMIT" NAME="processor" VALUE="reify_%s">
                </TD>"""  % (self.property_num, self.property_num))
        self.response.write("""
              </TR>
        """)

    def add(self, type):
        self.header("Add")
        self.response.write("""
          <FORM NAME="form" ACTION="edit" METHOD="POST">
            <TABLE>
              <TR>
                <TD VALIGN="TOP">URI</TD>
                <TD>&nbsp;</TD>
                <TD>
                  <INPUT TYPE="TEXT" SIZE="60" NAME="uri" value="%s"/>
                </TD>
              </TR>""" % (self.generateURI()))
        self.response.write("""
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
            self.response.write("""
                  <SELECT SIZE="1" NAME="type">
            """)
            for klass in self.storeNode.get(None, TYPE, CLASS):
                self.response.write("""
                    <OPTION VALUE="%s">%s</OPTION>
                """ % (klass[0], self.storeNode.label(klass[0])))
            self.response.write("""
                  </SELECT>
            """)
        else:
            self.response.write("""
                  <INPUT TYPE="HIDDEN" NAME="type" VALUE="%s"/>
                  %s
            """ % (type, self.link(type)))

            # TODO: make this a func... getProperties for subject?

            def possibleProperty(s, p, o, self=self):
                property = s
                if len(self.storeNode.get(property, self.REQUIREDPROPERTY, "http://redfoot.sourceforge.net/2000/10/06/builtin#YES"))>0:
                    self.editProperty(property, "", 0)

            self.storeNode.visitPossibleProperties(possibleProperty, type )

        self.response.write("""
                </TD>
              </TR>
        """)
        self.response.write("""
          </TABLE>
            <INPUT TYPE="HIDDEN" NAME="prop_count" VALUE="%s"/>
            <INPUT TYPE="HIDDEN" NAME="processor"  VALUE="create"/>
          <INPUT TYPE="SUBMIT"                   VALUE="create"/>
        """ % self.property_num)
        self.response.write("""
        </FORM>

              <P><A HREF="subclass">Return to List (without adding a Resource)</A></P>
        """)
        self.footer()

    def update(self, parameters):
        subject = parameters['uri']
        count = parameters['prop_count']
        i = 0
	self.storeNode.local.remove(subject)
        while i < int(count):
            i = i + 1
            property = parameters['prop%s_name' % i]
            value = parameters['prop%s_value' % i]
            isLiteral = parameters['prop%s_isLiteral' % i]
            if isLiteral == "yes":
                value = literal(value)
            self.storeNode.local.add(subject, property, value)
        newProperty = parameters['newProperty']
        newPropertyValue = ""
        if self.storeNode.getRange(newProperty)==LITERAL:
            newPropertyValue = literal(newPropertyValue)
        if newProperty!="":
            self.storeNode.local.add(subject, newProperty, newPropertyValue)

    def delete(self, parameters):
        subject = parameters['uri']
        if subject=="":
            raise "TODO: invalid subject"
        self.storeNode.local.remove(subject, None, None)

    def deleteProperty(self, parameters):
        property_num = parameters['processor'][4:]
        subject = parameters['uri']
        property = parameters['prop%s_name' % property_num]
        vName = "prop%s_value" % property_num
        value = parameters[vName]
        if self.storeNode.getRange(property)==LITERAL:
            value = literal(value)
        self.storeNode.local.remove(subject, property, value)

    def reifyProperty(self, parameters):
        property_num = parameters['processor'][6:]
        subject = parameters['uri']
        property = parameters['prop%s_name' % property_num]
        value = parameters['prop%s_value' % property_num]
        if self.storeNode.getRange(property)==LITERAL:
            value = literal(value)
        self.storeNode.reify(self.storeNode.local.URI+self.generateURI(), subject, property, value)

    def generateURI(self):
	import time
        return "#T%s" % time.time()

    def create(self, parameters):
        subject = parameters['uri']

        if subject[0]=="#":
            subject = self.storeNode.local.URI + subject

	self.storeNode.local.remove(subject)


        # TODO: what to do in the case it already exists?
        self.storeNode.local.add(subject, LABEL, literal(parameters['label']))
        self.storeNode.local.add(subject, TYPE, parameters['type'])

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
                value = literal(value)
            self.storeNode.local.add(subject, property, value)

    def save(self):
        self.storeNode.local.save()


#TODO: could be a separate module
class PeerEditor(Editor):

    def menuBar(self):
        Editor.menuBar(self)
        self.response.write("""
            <P CLASS="MENUBAR"><B>PEER</B>
             : <A HREF="connect">Connect Neighbour</A>
             |""")

        uri = self.request.getParameters()['uri']
        if uri!="":
            uriqs = "&uri=%s" % self.encodeURI(uri)
        else:
            uriqs = ""

        if self.showNeighbours==1:
            self.response.write("""
            <A HREF="?processor=hideNeighbours%s">Hide Neighbour Resources</A>""" % uriqs)
        else:
            self.response.write("""
            <A HREF="?processor=showNeighbours%s">Show Neighbour Resources</A>""" % uriqs)

        self.response.write("""
            </P>
        """)
    
    def connectPage(self):
        self.header("Connect Neighbour")
        self.response.write("""
              <FORM NAME="form" ACTION="subclass" METHOD="POST">
                <P>URI to Connect: <INPUT TYPE="TEXT" NAME="uri" SIZE="60">
                <INPUT TYPE="SUBMIT" NAME="processor"  VALUE="connect"/>
                </P>
              </FORM>
        """)
        self.footer()

    def connect(self, parameters):
        uri = parameters["uri"]
        if uri!="":
            self.storeNode.connectTo(uri)


#~ $Log$
#~ Revision 5.11  2000/12/20 04:04:39  jtauber
#~ fixed typo in encodeAttributeValue name
#~
#~ Revision 5.10  2000/12/20 03:35:28  jtauber
#~ can now delete empty properties of range LITERAL
#~
#~ Revision 5.9  2000/12/20 03:14:48  jtauber
#~ added encoding of special chars in attribute values and character data
#~
#~ Revision 5.8  2000/12/19 16:35:41  eikeon
#~ changed neighbourhood to neighbours in one place
#~
#~ Revision 5.7  2000/12/17 23:58:44  eikeon
#~ recatored to use header and footer methods
#~
#~ Revision 5.6  2000/12/17 23:41:58  eikeon
#~ removed of log messages
#~
#~ Revision 5.5  2000/12/14 05:16:16  eikeon
#~ converted a method to new query interface
#~
#~ Revision 5.4  2000/12/14 00:13:36  eikeon
#~ fixed typo
#~
#~ Revision 5.3  2000/12/13 02:54:11  jtauber
#~ moved functions in query around and renamed a lot
#~
#~ Revision 5.2  2000/12/09 23:02:12  jtauber
#~ fixed font-weight and size
#~
#~ Revision 5.1  2000/12/09 22:08:33  eikeon
#~ subclass -> fullsubclass; subclassNR -> subclass
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
