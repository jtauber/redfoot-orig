# $Header$

from redfoot.viewer import Viewer
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
            request.setPathInfo(path_info)
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
        """ % (self.encodeCharacterData(self.storeNode.label(subject)), subject, self.encodeURI(subject), self.encodeURI(subject)))

    def edit(self, parameters):
	subject = parameters['uri']
	type = parameters['type']
	copy = parameters['copy']

	if copy!=None and copy=="copy":
            subject = self.storeNode.local.URI + self.generateURI()
	    self.update(parameters, subject, copy=1)
        if subject==None or subject=="":
            subject = self.storeNode.local.URI + self.generateURI()
        if type!=None and type!="":
            self.storeNode.local.add(subject, TYPE, type)

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
        else:
            self.response.write("""<TR><TD>Resource not known of directly</TD></TR>""")

        properties = {}
        def possibleProperty(s, p, o, properties=properties):
            properties[s] = 1
        self.storeNode.visitPossiblePropertiesForSubject(possibleProperty, subject)
        
        for property in properties.keys():
            if len(self.storeNode.get(property, self.REQUIREDPROPERTY, "http://redfoot.sourceforge.net/2000/10/06/builtin#YES"))>0 and len(self.storeNode.get(subject, property, None))==0:   
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
                                """ % (s, self.storeNode.label(s)))
        self.storeNode.visitPossiblePropertiesForSubject(possibleProperty, subject)


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
                self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_orig" VALUE="%s">
            """ % (self.property_num, un_literal(value)))                
            else:
                self.response.write("""
                <INPUT TYPE="TEXT" SIZE="60" NAME="prop%s_value" VALUE="%s">
                """ % (self.property_num, self.encodeAttributeValue(un_literal(value))))
                self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_orig" VALUE="%s">
            """ % (self.property_num, self.encodeAttributeValue(un_literal(value))))
            self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_isLiteral" VALUE="yes">
            """ % self.property_num)
        else:
            rangelist = self.storeNode.get(property, RANGE, None) # already did this above
            if len(rangelist) > 0:
                self.response.write("""
                    <INPUT TYPE="HIDDEN" NAME="prop%s_orig" VALUE="%s">
            """ % (self.property_num, value))                
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
            h = "Add a " + self.storeNode.label(type)
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
                orig = literal(orig)
            if copy:
                self.storeNode.local.add(subject, property, value)
            elif value!=orig:
                self.storeNode.local.remove(subject, property, orig)
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
        vName = "prop%s_orig" % property_num
        value = parameters[vName]
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
	#import time
        #return "#T%s" % time.time()
        return date_time_path()

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
#~ Revision 6.5  2001/03/15 16:47:51  eikeon
#~ The recent change to update broke copy... it is now fixed.
#~
#~ Revision 6.4  2001/03/13 19:55:44  eikeon
#~ orig was not getting set for things of type resource... now it is
#~
#~ Revision 6.3  2001/02/27 20:55:07  eikeon
#~ update no longer removes and re-adds properties who's values are unchanged; generateURI changed
#~
#~ Revision 6.2  2001/02/26 22:41:03  eikeon
#~ removed old log messages
#~
#~ Revision 6.1  2001/02/20 19:10:47  eikeon
#~ added missing 'self.'
#~
#~ Revision 6.0  2001/02/19 05:01:23  jtauber
#~ new release
