# $Header$

from redfoot.modules.viewer import Viewer
from rdf.literal import literal, un_literal, is_literal

from rdf.const import *

def date_time_path(t=None):
    """."""
    import time
    if t==None:
        t = time.time()

    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
    s = "%0004d/%02d/%02d/T%02d/%02d/%02dZ" % ( year, month, day, hh, mm, ss)        
    return s

class Editor(Viewer):

    def handle_request(self, request, response):
        self.response = response
        self.request = request
        
        parameters = request.getParameters()
        path_info = request.getPathInfo()

        processor = parameters['processor']
        if processor == "update":
            self.update(parameters)
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
            self.edit(parameters)
	elif path_info == "/add":
            self.add(parameters['type'])
        elif path_info == "/connect":
            self.connectPage()
        else:
            Viewer.handle_request(self, request, response)

    def menuBar(self):
        Viewer.menuBar(self)
        self.response.write("""
            <P CLASS="MENUBAR"><B>EDIT</B>
             : <A HREF="add">Add an External Resource</A>
             | <A HREF="edit">Create an Abstract Resource</A>
             | <A HREF="?processor=save">Save Node to Disk</A>
            </P>
        """)

    def resourceHeader(self, subject):
        self.response.write("""
            <H3>%s</H3>
            <P>%s - <A HREF="view?uri=%s">view</A>|<A HREF="edit?uri=%s">edit</A>
        """ % (self.encodeCharacterData(self.rednode.label(subject)), subject, self.encodeURI(subject), self.encodeURI(subject)))

    def edit(self, parameters):
	subject = parameters['uri']
	type = parameters['type']
	copy = parameters['copy']

	if copy!=None and copy=="copy":
            subject = self.rednode.local.URI + self.generateURI()
	    self.update(parameters, subject, copy=1)
        if subject==None or subject=="":
            subject = self.rednode.local.URI + self.generateURI()
        if type!=None and type!="":
            self.rednode.local.add(subject, TYPE, type)

        self.header("Edit")
        self.resourceHeader(subject)
        self.response.write("""
            <FORM NAME="form" ACTION="edit?uri=%s" METHOD="POST">
              <INPUT NAME="uri" TYPE="HIDDEN" VALUE="%s">
              <TABLE>
        """ % (subject, subject))
        self.property_num = 0

        if self.rednode.isKnownResource(subject):
            self.rednode.local.visitPredicateObjectPairsForSubject(self.editProperty, subject)
            self.rednode.neighbours.visitPredicateObjectPairsForSubject(self.displayPropertyValue, subject)
	    self.rednode.visitReifiedStatementsAboutSubject(self.displayReifiedStatements, subject)
        else:
            self.response.write("""<TR><TD>Resource not known of directly</TD></TR>""")

        properties = {}
        def possibleProperty(s, p, o, properties=properties):
            properties[s] = 1
        self.rednode.visitPossiblePropertiesForSubject(possibleProperty, subject)
        
        for property in properties.keys():
            if len(self.rednode.get(property, self.REQUIREDPROPERTY, "http://redfoot.sourceforge.net/2000/10/06/builtin#YES"))>0 and len(self.rednode.get(subject, property, None))==0:   
                self.editProperty(property, "", 0)   
    
        self.response.write("""
          <TR>
            <TD>
              <SELECT type="text" name="newProperty">

                <OPTION value="">Select a new Property to add</OPTION>
        """)

        def possibleProperty(s, p, o, self=self):
            self.response.write("""
                <OPTION value="%s">%s</OPTION>
                                """ % (s, self.rednode.label(s)))
        self.rednode.visitPossiblePropertiesForSubject(possibleProperty, subject)


        self.response.write("""
              </SELECT>

            </TD>

            <TD COLSPAN="5">Click update to be able to specify value</TD>
          </TR>

        </TABLE>

        <INPUT TYPE="HIDDEN" NAME="prop_count" VALUE="%s">
        <INPUT TYPE="SUBMIT" NAME="processor"  VALUE="update">
        <INPUT TYPE="SUBMIT" NAME="processor"  VALUE="delete">
        <INPUT TYPE="SUBMIT" NAME="copy"  VALUE="copy" ONCLICK="form.action='edit'; form.submit()">
      </FORM>
          """ % self.property_num)

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
        """ % (self.rednode.label(property), self.property_num, property))

        def callback(s, p, o, self=self):
            self.response.write("%s<BR>" % self.rednode.label(o))
        self.rednode.visit(callback, property, RANGE, None)

        self.response.write("""
                  </TD>
                  <TD COLSPAN="2">
        """)
        if (len(value) > 0 and is_literal(value[0])) or (len(value)==0 and self.rednode.getRange(property)==LITERAL):
            uitype = self.rednode.getFirst(property, self.UITYPE, None)
            if uitype != None and uitype[2]==self.TEXTAREA:
                self.response.write("""
                <TEXTAREA NAME="prop%s_value" ROWS="5" COLS="60">%s</TEXTAREA>
                """ % (self.property_num, un_literal(value)))
                self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_orig" VALUE="%s">
            """ % (self.property_num, self.encodeAttributeValue(value)))                
            else:
                self.response.write("""
                <INPUT TYPE="TEXT" SIZE="60" NAME="prop%s_value" VALUE="%s">
                """ % (self.property_num, self.encodeAttributeValue(un_literal(value))))
                self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_orig" VALUE="%s">
            """ % (self.property_num, self.encodeAttributeValue(value)))
            self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_isLiteral" VALUE="yes">
            """ % self.property_num)
        else:
            rangelist = self.rednode.get(property, RANGE, None) # already did this above
            if len(rangelist) > 0:
                self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_orig" VALUE="%s">
            """ % (self.property_num, self.encodeAttributeValue(value)))
                self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_isLiteral" VALUE="no">
                    <SELECT NAME="prop%s_value">
                      <OPTION value="">Select a value for this property</OPTION>
                """ % (self.property_num, self.property_num))


                possibleValues = {}
                def possibleValue(s, p, o, rednode=self.rednode, possibleValues=possibleValues):
                    label = rednode.label(s)
                    # we use a key of 'label + s' to insure uniqness of key
                    possibleValues[label+s] = s 

                self.rednode.visitPossibleValues(possibleValue, property)

                pvs = possibleValues.keys()
                pvs.sort()

                for pv in pvs:
                    v = possibleValues[pv]
                    if v==value:
                        self.response.write("""
                        <OPTION SELECTED="TRUE" VALUE="%s">%s</OPTION>
                        """ % (v, self.rednode.label(v)))
                    else:
                        self.response.write("""
                        <OPTION VALUE="%s">%s</OPTION>
                        """ % (v, self.rednode.label(v)))
                    


                self.response.write("""
                    </SELECT>
                """)
            else:
                #TODO 
                self.response.write("""
                    <INPUT TYPE="TEXT" SIZE="60" NAME="prop%s_value" VALUE="%s">***
                """ % (self.property_num, self.encodeAttributeValue(value)))
                self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_orig" VALUE="%s">
            """ % (self.property_num, self.encodeAttributeValue(value)))
                
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
        h = "Add"
        if type!=None and type!="":
            h = "Add a " + self.rednode.label(type)
        self.header(h)
        self.response.write("""
          <FORM NAME="form" ACTION="edit" METHOD="POST">
            <TABLE>
              <TR>
                <TD VALIGN="TOP">URI</TD>
                <TD>&nbsp;</TD>
                <TD>
                  <INPUT TYPE="TEXT" SIZE="60" NAME="uri">
                </TD>
              </TR>
          </TABLE>
          <INPUT TYPE="SUBMIT" VALUE="create">
          <INPUT TYPE="HIDDEN" NAME="type" VALUE="%s">
        </FORM>
              <P><A HREF="subclass">Return to List (without adding a Resource)</A></P>
        """ % type)
        self.footer()

    def update(self, parameters, subject=None, copy=0):
	if subject==None:
	    subject = parameters['uri']
        count = parameters['prop_count']
        i = 0
        while i < int(count):
            i = i + 1
            property = parameters['prop%s_name' % i]
            value = parameters['prop%s_value' % i]
            orig = parameters['prop%s_orig' % i]            
            isLiteral = parameters['prop%s_isLiteral' % i]
            if isLiteral == "yes":
                value = literal(value)
            if copy:
                self.rednode.local.add(subject, property, value)
            elif value!=orig:
                self.rednode.local.remove(subject, property, orig)
                self.rednode.local.add(subject, property, value)
        newProperty = parameters['newProperty']
        newPropertyValue = ""
        if self.rednode.getRange(newProperty)==LITERAL:
            newPropertyValue = literal(newPropertyValue)
        if newProperty!="":
            self.rednode.local.add(subject, newProperty, newPropertyValue)

    def delete(self, parameters):
        subject = parameters['uri']
        if subject=="":
            raise "TODO: invalid subject"
        self.rednode.local.remove(subject, None, None)

    def deleteProperty(self, parameters):
        property_num = parameters['processor'][4:]
        subject = parameters['uri']
        property = parameters['prop%s_name' % property_num]
        vName = "prop%s_orig" % property_num
        value = parameters[vName]
        self.rednode.local.remove(subject, property, value)

    def reifyProperty(self, parameters):
        property_num = parameters['processor'][6:]
        subject = parameters['uri']
        property = parameters['prop%s_name' % property_num]
        value = parameters['prop%s_value' % property_num]
        if self.rednode.getRange(property)==LITERAL:
            value = literal(value)
        self.rednode.reify(self.rednode.local.URI+self.generateURI(), subject, property, value)

    def generateURI(self):
	#import time
        #return "#T%s" % time.time()
        return date_time_path()

    def save(self):
        self.rednode.local.save()


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
            self.rednode.connectTo(uri)


#~ $Log$
#~ Revision 1.1  2001/04/14 23:40:28  eikeon
#~ created a lib/redfoot/modules directory and moved editor/viewer into it
#~
#~ Revision 7.4  2001/04/14 23:10:28  eikeon
#~ removed old log messages
#~
#~ Revision 7.3  2001/04/12 09:06:48  jtauber
#~ added TODO
#~
#~ Revision 7.2  2001/04/11 16:05:10  jtauber
#~ seemed to miss a few storeNode->rednode
#~
#~ Revision 7.1  2001/04/09 17:25:02  eikeon
#~ storeNode -> rednode
#~
#~ Revision 7.0  2001/03/26 23:41:05  eikeon
#~ NEW RELEASE
