# $Header$

from redfoot.viewer import Viewer
from rdf.literal import literal, un_literal, is_literal

from rdf.const import *

class Editor(Viewer):

    def handleRequest(self, request, response):
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
            <H3>%s</H3>
            <P>%s - <A HREF="view?uri=%s">view</A>|<A HREF="edit?uri=%s">edit</A>
        """ % (self.storeNode.label(subject), subject, self.encodeURI(subject), self.encodeURI(subject)))

    def edit(self, subject):
        if subject!=None and subject!="" and subject[0]=="#":
            subject = self.storeNode.local.URI + subject

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

        if self.storeNode.isKnownResource(subject):
            self.storeNode.local.visitPredicateObjectPairsForSubject(self.editProperty, subject)
            self.storeNode.neighbourhood.visitPredicateObjectPairsForSubject(self.displayPropertyValue, subject)
        
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
                """ % (self.property_num, un_literal(value)))
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
            </BODY>
          </HTML>
        """)

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
        if newProperty!="":
            self.storeNode.local.add(subject, newProperty, "")

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
        
              <FORM NAME="form" ACTION="subclass" METHOD="POST">
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
            self.storeNode.connectTo(uri)


# $Log$
# Revision 5.4  2000/12/14 00:13:36  eikeon
# fixed typo
#
# Revision 5.3  2000/12/13 02:54:11  jtauber
# moved functions in query around and renamed a lot
#
# Revision 5.2  2000/12/09 23:02:12  jtauber
# fixed font-weight and size
#
# Revision 5.1  2000/12/09 22:08:33  eikeon
# subclass -> fullsubclass; subclassNR -> subclass
#
# Revision 5.0  2000/12/08 08:34:52  eikeon
# new release
#
# Revision 4.13  2000/12/08 07:39:12  eikeon
# show / hide does not lose current value for uri paramter
#
# Revision 4.12  2000/12/07 17:54:04  eikeon
# Viewer (and Editor, PeerEditor) no longer have both a qstore and a storeNode
#
# Revision 4.11  2000/12/06 23:26:55  eikeon
# Made rednode consistently be the local plus neighbourhood; neighbourhood be only the neighbours; and local be only the local part -- much less confusing
#
# Revision 4.10  2000/12/06 21:25:16  eikeon
# editor now uses getRange where possible; also now uses is_literal/literal where possible
#
# Revision 4.9  2000/12/06 20:50:31  eikeon
# Now uses the new getPossibleProperties* methods on query
#
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
