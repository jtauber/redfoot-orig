# $Header$

from redfoot.viewer import Viewer
from rdf.literal import literal, un_literal, is_literal

from rdf.const import *

class Editor(Viewer):

    def handleRequest(self, request, response):
        self.response = response
        
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
            Viewer.handleRequest(self, request, response)


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
            <H2>%s</H2>
            <P>%s - <A HREF="view?uri=%s">view</A>|<A HREF="edit?uri=%s">edit</A>
        """ % (self.qstore.neighbourhood.label(subject), subject, self.encodeURI(subject), self.encodeURI(subject)))

    def edit(self, subject):
        if subject!=None and subject!="" and subject[0]=="#":
            subject = self.qstore.URI + subject

        self.response.write("""
          <HTML>
            <HEAD>
              <TITLE>ReDFoot: Edit</TITLE>
              <LINK REL="STYLESHEET" HREF="css"/>
            </HEAD>
            <BODY>
              <H1>ReDFoot</H1>""")
        self.menuBar()
        self.resourceHeader(subject)
        self.response.write("""
            <H3>Edit</H3>
            <FORM NAME="form" ACTION="edit?uri=%s" METHOD="POST">
              <INPUT NAME="uri" TYPE="HIDDEN" VALUE="%s">
              <TABLE>
        """ % (subject, subject))
        self.property_num = 0

        if self.qstore.isKnownResource(subject):
            self.qstore.propertyValuesV(subject, self.editProperty)
            self.qstore.neighbourhood.stores.propertyValuesV(subject, self.displayPropertyValue)
        
	    self.qstore.reifiedV(subject, self.displayReifiedStatements)

            self.response.write("""
              <TR>
                <TD>
                  <SELECT type="text" name="newProperty">

                    <OPTION value="">Select a new Property to add</OPTION>
            """)

            def possibleProperty(s, p, o, self=self):
                self.response.write("""
                    <OPTION value="%s">%s</OPTION>
                                    """ % (s, self.qstore.neighbourhood.label(s)))
            self.qstore.neighbourhood.getPossiblePropertiesForSubject(subject, possibleProperty)


            def option(s, p, o, write=self.response.write, neighbourhood=self.qstore.neighbourhood):
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

        self.response.write("""
        </BODY>
      </HTML>
      """)

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
        """ % (self.qstore.neighbourhood.label(property), self.property_num, property))

        def callback(s, p, o, self=self):
            self.response.write("%s<BR>" % self.qstore.neighbourhood.label(o))
        self.qstore.neighbourhood.visit(callback, property, RANGE, None)

        self.response.write("""
                  </TD>
                  <TD COLSPAN="2">
        """)
        if (len(value) > 0 and value[0]=="^") or (len(value)==0 and self.qstore.neighbourhood.get(property, RANGE, None)[0][2]==LITERAL):
            uitype = self.qstore.neighbourhood.get(property, self.UITYPE, None)
            if len(uitype) > 0 and uitype[0][2]==self.TEXTAREA:
                self.response.write("""
                <TEXTAREA NAME="prop%s_value" ROWS="5" COLS="60">%s</TEXTAREA>
                """ % (self.property_num, un_literal(value)))
            else:
                self.response.write("""
                <INPUT TYPE="TEXT" SIZE="60" NAME="prop%s_value" VALUE="%s">
                """ % (self.property_num, un_literal(value)))
            self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_isLiteral" VALUE="yes">
            """ % self.property_num)
        else:
            rangelist = self.qstore.neighbourhood.get(property, RANGE, None) # already did this above
            if len(rangelist) > 0:
                self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_isLiteral" VALUE="no">
                    <SELECT NAME="prop%s_value">
                      <OPTION value="">Select a value for this property</OPTION>
                """ % (self.property_num, self.property_num))


                possibleValues = {}
                def possibleValue(s, p, o, qstore=self.qstore, possibleValues=possibleValues):
                    label = qstore.neighbourhood.label(s)
                    # we use a key of 'label + s' to insure uniqness of key
                    possibleValues[label+s] = s 

                self.qstore.neighbourhood.getPossibleValuesV(property, possibleValue)

                pvs = possibleValues.keys()
                pvs.sort()

                for pv in pvs:
                    v = possibleValues[pv]
                    if v==value:
                        self.response.write("""
                        <OPTION SELECTED="TRUE" VALUE="%s">%s</OPTION>
                        """ % (v, self.qstore.neighbourhood.label(v)))
                    else:
                        self.response.write("""
                        <OPTION VALUE="%s">%s</OPTION>
                        """ % (v, self.qstore.neighbourhood.label(v)))
                    


                self.response.write("""
                    </SELECT>
                """)
            else:
                self.response.write("""
                    <INPUT TYPE="TEXT" SIZE="60" NAME="prop%s_value" VALUE="%s">***
                """ % (self.property_num, value))
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
        self.response.write("""
          <HTML>
            <HEAD>
              <TITLE>ReDFoot: Add</TITLE>
              <LINK REL="stylesheet" HREF="css"/>
            </HEAD>
            <BODY>
              <H1>ReDFoot</H1>""")
        self.menuBar()
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
            for klass in self.qstore.neighbourhood.get(None, TYPE, CLASS):
                self.response.write("""
                    <OPTION VALUE="%s">%s</OPTION>
                """ % (klass[0], self.qstore.neighbourhood.label(klass[0])))
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
                if len(self.qstore.neighbourhood.get(property, self.REQUIREDPROPERTY, "http://redfoot.sourceforge.net/2000/10/06/builtin#YES"))>0:
                    self.editProperty(property, "", 0)

            self.qstore.neighbourhood.getPossibleProperties(type, possibleProperty)

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

              <P><A HREF="subclassNR">Return to List (without adding a Resource)</A></P>
            </BODY>
          </HTML>
        """)

    def update(self, parameters):
        subject = parameters['uri']
        count = parameters['prop_count']
        i = 0
	self.qstore.remove(subject)
        while i < int(count):
            i = i + 1
            property = parameters['prop%s_name' % i]
            value = parameters['prop%s_value' % i]
            isLiteral = parameters['prop%s_isLiteral' % i]
            if isLiteral == "yes":
                value = "^" + value
            self.qstore.add(subject, property, value)
        newProperty = parameters['newProperty']
        if newProperty!="":
            self.qstore.add(subject, newProperty, "")

    def delete(self, parameters):
        subject = parameters['uri']
        if subject=="":
            raise "TODO: invalid subject"
        self.qstore.remove(subject, None, None)

    def deleteProperty(self, parameters):
        property_num = parameters['processor'][4:]
        subject = parameters['uri']
        property = parameters['prop%s_name' % property_num]
        vName = "prop%s_value" % property_num
        value = parameters[vName]
        if self.qstore.neighbourhood.get(property, RANGE, None)[0][2]==LITERAL:
            value = "^" + value
        self.qstore.remove(subject, property, value)

    def reifyProperty(self, parameters):
        property_num = parameters['processor'][6:]
        subject = parameters['uri']
        property = parameters['prop%s_name' % property_num]
        value = parameters['prop%s_value' % property_num]
        if self.qstore.neighbourhood.get(property, RANGE, None)[0][2]==LITERAL:
            value = "^" + value
        self.qstore.reify(self.storeNode.URI+self.generateURI(), subject, property, value)

    def generateURI(self):
	import time
        return "#T%s" % time.time()

    def create(self, parameters):
        subject = parameters['uri']

        if subject[0]=="#":
            subject = self.qstore.URI + subject

	self.qstore.remove(subject)


        # TODO: what to do in the case it already exists?
        self.qstore.add(subject, LABEL, "^"+parameters['label'])
        self.qstore.add(subject, TYPE, parameters['type'])

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
            self.qstore.add(subject, property, value)

    def save(self):
        self.qstore.save()


#TODO: could be a separate module
class PeerEditor(Editor):

    def menuBar(self):
        Editor.menuBar(self)
        self.response.write("""
            <P CLASS="MENUBAR"><B>PEER</B>
             : <A HREF="connect">Connect Neighbour</A>
             |""")

        if self.showNeighbours==1:
            self.response.write("""
            <A HREF="?processor=hideNeighbours">Hide Neighbour Resources</A>""")
        else:
            self.response.write("""
            <A HREF="?processor=showNeighbours">Show Neighbour Resources</A>""")

        self.response.write("""
            </P>
        """)
    
    def connectPage(self):
        self.response.write("""
          <HTML>
            <HEAD>
              <TITLE>ReDFoot: Connect</TITLE>
              <LINK REL="STYLESHEET" HREF="css"/>
            </HEAD>
            <BODY>
              <H1>ReDFoot</H1>""")
        self.menuBar()
        self.response.write("""
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
            self.qstore.connectTo(uri)


# $Log$
# Revision 4.8  2000/12/05 22:43:30  eikeon
# moved constants to rdf.const
#
# Revision 4.7  2000/12/05 07:11:27  eikeon
# finished refactoring rednode refactor of the local / neighbourhood split
#
# Revision 4.6  2000/12/05 03:49:07  eikeon
# changed all the hardcoded [1:] etc stuff to use un_literal is_literal etc
#
# Revision 4.5  2000/12/05 00:02:25  eikeon
# fixing some of the local / neighbourhood stuff
#
# Revision 4.4  2000/12/04 22:07:35  eikeon
# got rid of all the getStore().getStore() stuff by using Multiple inheritance and mixin classes instead of all the classes being wrapper classes
#
# Revision 4.3  2000/12/04 22:00:59  eikeon
# got rid of all the getStore().getStore() stuff by using Multiple inheritance and mixin classes instead of all the classes being wrapper classes
#
# Revision 4.2  2000/11/27 19:39:10  eikeon
# editor now alphabetically sort possible values for properties
#
# Revision 4.1  2000/11/21 16:49:01  eikeon
# fixed VALIGN=top typo on reify buttons
#
# Revision 4.0  2000/11/06 15:57:34  eikeon
# VERSION 4.0
#
# Revision 3.6  2000/11/04 03:39:10  eikeon
# moved sample authentication from editor.py to sample.py
#
# Revision 3.5  2000/11/04 01:25:33  eikeon
# removed old log messaged
#
# Revision 3.4  2000/11/03 23:04:08  eikeon
# Added support for cookies and sessions; prefixed a number of methods and variables with _ to indicate they are private; changed a number of methods to mixed case for consistency; added a setHeader method on response -- headers where hardcoded before; replaced writer with response as writer predates and is redundant with repsonse; Added authentication to editor
#
# Revision 3.3  2000/11/02 21:00:56  eikeon
# fixed bug that was causing problems when trying to save when on the edit page
#
# Revision 3.2  2000/10/31 05:03:08  eikeon
# mainly Refactored how parameters are accessed (no more [0]'s); some cookie code; a few minor changes regaurding plumbing
#
# Revision 3.1  2000/10/29 01:54:35  eikeon
# fixed Unknown Attribute property_num bug I introduced just before 0.9.1 ;(
#
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
