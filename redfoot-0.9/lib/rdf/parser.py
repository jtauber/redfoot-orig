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

from rdf.const import *

from rdf.literal import literal, is_literal

class HandlerBase:
    def __init__(self, parser, adder, parent):
        self.parser = parser
        self.adder = adder
        self.parent = parent
        self.setHandlers()

    def setHandlers(self):
        pass

    def char(self, data):
        pass

    def child(self, name, atts):
        pass
    
    def end(self, name):
        self.parent.setHandlers()

    
class RootHandler(HandlerBase):
    def __init__(self, parser, adder, parent):
        HandlerBase.__init__(self, parser, adder, parent)

    def child(self, name, atts):
        if name==RDFNS+"RDF":
            RDFHandler(self.parser, self.adder, self)
        else:
            pass

    def setHandlers(self):
        self.parser.StartElementHandler = self.child


class RDFHandler(HandlerBase):
    def __init__(self, parser, adder, parent):
        HandlerBase.__init__(self, parser, adder, parent)

    def setHandlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        if name==RDFNS+"Description":
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
        elif atts.has_key(RDFNS+"about"):
            self.subject = atts[RDFNS+"about"]
        elif atts.has_key(RDFNS+"ID"):
            self.subject = self.parser.GetBase() + "#" + atts[RDFNS+"ID"]
        else:
            import sys
            sys.stderr.write("Descriptions must have either an about or an ID\n")
            
        for att in atts.keys():
            if att=="about" or att=="ID" or att==RDFNS+"about" or att==RDFNS+"ID":
                pass
            else:
                self.adder(self.subject, att, literal(atts[att]))

    def setHandlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        PropertyHandler(self.parser, self.adder, self, name, atts)
                        

class TypedNodeHandler(DescriptionHandler):
    def __init__(self, parser, adder, parent, name, atts):
        DescriptionHandler.__init__(self, parser, adder, parent, atts)
        self.adder(self.subject, RDFNS+"type", name)


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
        elif atts.has_key(RDFNS+"resource"):
            self.object = atts[RDFNS+"resource"]
            if self.object[0]=="#":
                self.object = self.parser.GetBase() + self.object
            for att in atts.keys():
                if att == RDFNS+"resource":
                    pass
                else:
                    self.adder(self.object, att, literal(atts[att]))
        else:
            self.object = literal("")

    def setHandlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        if name==RDFNS+"Description":
            self.object = atts["about"]
            DescriptionHandler(self.parser, self.adder, self, atts)
        else:
            pass

    def char(self, data):
        self.object = self.object + data

    def end(self, name):
        self.adder(self.parent.subject, self.predicate, self.object)
        self.parent.setHandlers()

#~ $Log$
#~ Revision 5.1  2000/12/17 20:40:47  eikeon
#~ started adding exception handling code around parse
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
