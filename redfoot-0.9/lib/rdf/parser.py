# $Header$

def parse_RDF(adder, location, baseURI=None):
    if baseURI==None:
        baseURI = location

    import pyexpat
    parser = pyexpat.ParserCreate(namespace_separator="")

    parser.SetBase(baseURI)
    RootHandler(parser, adder, None)

    #parser.returns_unicode = 0
    from urllib import urlopen
    f = urlopen(location)
    try:
        parser.ParseFile(f)
    except: # pyexpat.error:
        import sys
        sys.stderr.write("Error parsing file at line '%s' and column '%s'\n" % (parser.ErrorLineNumber, parser.ErrorColumnNumber) )
        sys.stderr.flush()
    f.close()

from rdf.const import RDFNS
from rdf.const import TYPE

RDF = RDFNS+"RDF"
DESCRIPTION = RDFNS+"Description"
ABOUT = RDFNS+"about"
ID = RDFNS+"ID"
RESOURCE = RDFNS+"resource"

from rdf.literal import literal, is_literal

class HandlerBase:
    def __init__(self, parser, adder, parent):
        self.parser = parser
        self.adder = adder
        self.parent = parent
        self.set_handlers()

    def set_handlers(self):
        pass

    def char(self, data):
        pass

    def child(self, name, atts):
        pass
    
    def end(self, name):
        self.parent.set_handlers()

    
class RootHandler(HandlerBase):
    def __init__(self, parser, adder, parent):
        HandlerBase.__init__(self, parser, adder, parent)
        self.found_root = 0
        self.depth = 0

    def child(self, name, atts):
        self.depth = self.depth + 1
        if name==RDF:
            if self.found_root==0:
                self.found_root = 1
                RDFHandler(self.parser, self.adder, self)
            else:
                import sys
                sys.stderr.write("warning: found more than one %s element" % RDF)
                # TODO: is this a valid situation?
                RDFHandler(self.parser, self.adder, self)
        else:
            pass

    def end(self, name):
        self.depth = self.depth - 1
        if self.depth==0 and self.found_root==0:
            import sys
            sys.stderr.write("warning: Did not find a '%s' element\n" % RDF)
            sys.stderr.flush()

    def set_handlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.EndElementHandler = self.end


class RDFHandler(HandlerBase):
    def __init__(self, parser, adder, parent):
        HandlerBase.__init__(self, parser, adder, parent)

    def set_handlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        if name==DESCRIPTION:
            DescriptionHandler(self.parser, self.adder, self, atts)
        else:
            TypedNodeHandler(self.parser, self.adder, self, name, atts)

        
class DescriptionHandler(HandlerBase):
    def __init__(self, parser, adder, parent, atts):
        HandlerBase.__init__(self, parser, adder, parent)
        self.subject = None
        if atts.has_key("about"):
            self.subject = atts["about"]
        elif atts.has_key("ID"):
            self.subject = self.parser.GetBase() + "#" + atts["ID"]
        elif atts.has_key(ABOUT):
            self.subject = atts[ABOUT]
        elif atts.has_key(ID):
            self.subject = self.parser.GetBase() + "#" + atts[ID]
        else:
            import sys
            sys.stderr.write("Descriptions must have either an about or an ID\n")
            
        for att in atts.keys():
            if att=="about" or att=="ID" or att==ABOUT or att==ID:
                pass
            else:
                self.adder(self.subject, att, literal(atts[att]))

    def set_handlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        PropertyHandler(self.parser, self.adder, self, name, atts)
                        

class TypedNodeHandler(DescriptionHandler):
    def __init__(self, parser, adder, parent, name, atts):
        DescriptionHandler.__init__(self, parser, adder, parent, atts)
        self.adder(self.subject, TYPE, name)


class PropertyHandler(HandlerBase):
    def __init__(self, parser, adder, parent, name, atts):    
        HandlerBase.__init__(self, parser, adder, parent)
        self.predicate = name
        if atts.has_key("resource"):
            self.object = atts["resource"]
            if self.object[0]=="#":
                self.object = self.parser.GetBase() + self.object
            for att in atts.keys():
                if att == "resource":
                    pass
                else:
                    self.adder(self.object, att, literal(atts[att]))
        elif atts.has_key(RESOURCE):
            self.object = atts[RESOURCE]
            if self.object[0]=="#":
                self.object = self.parser.GetBase() + self.object
            for att in atts.keys():
                if att == RESOURCE:
                    pass
                else:
                    self.adder(self.object, att, literal(atts[att]))
        else:
            self.object = literal("")

    def set_handlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        if name==DESCRIPTION:
            self.object = atts["about"]
            DescriptionHandler(self.parser, self.adder, self, atts)
        else:
            pass

    def char(self, data):
        self.object = self.object + data

    def end(self, name):
        self.adder(self.parent.subject, self.predicate, self.object)
        self.parent.set_handlers()

#~ $Log$
#~ Revision 5.4  2000/12/22 22:25:35  eikeon
#~ moved definition and calculation of RDF (xml vocab) constants out of 'inner parsing loop'
#~
#~ Revision 5.3  2000/12/20 20:37:17  eikeon
#~ changed mixed case to _ style... all except for query
#~
#~ Revision 5.2  2000/12/17 21:11:11  eikeon
#~ changed a couple mixed case names to _ style names
#~
#~ Revision 5.1  2000/12/17 20:40:47  eikeon
#~ started adding exception handling code around parse
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
