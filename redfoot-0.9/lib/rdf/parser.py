# $Header$

from string import split, join

def hack_around(name, atts):
    new_name = join(split(name, '^'), '')
    new_atts = {}
    for key in atts.keys():
        new_key = join(split(key, '^'), '')
        new_atts[new_key] = atts[key]
    return (new_name, new_atts)

def parse_RDF(adder, location, baseURI=None):
    if baseURI==None:
        baseURI = location

    import pyexpat
    parser = pyexpat.ParserCreate(namespace_separator="^")

    parser.SetBase(baseURI)
    RootHandler(parser, adder, None)

    parser.returns_unicode = 1
    from urllib import urlopen
    f = urlopen(location)
    try:
        parser.ParseFile(f)
    except: # pyexpat.error:
        import sys
        import traceback
        traceback.print_exc()
        sys.stderr.flush()
        sys.stderr.write(u"Error parsing file at line '%s' and column '%s'\n" % (parser.ErrorLineNumber, parser.ErrorColumnNumber) )
        sys.stderr.flush()
    f.close()

def parse_RDF_stream(adder, stream, baseURI=None):
    if baseURI==None:
        baseURI = location

    import pyexpat
    parser = pyexpat.ParserCreate(namespace_separator="^")

    parser.SetBase(baseURI)
    RootHandler(parser, adder, None)

    parser.returns_unicode = 1
    try:
        parser.ParseFile(stream)
    except: # pyexpat.error:
        import sys
        import traceback
        traceback.print_exc()
        sys.stderr.flush()
        sys.stderr.write(u"Error parsing file at line '%s' and column '%s'\n" % (parser.ErrorLineNumber, parser.ErrorColumnNumber) )
        sys.stderr.flush()
    stream.close()

from rdf.const import RDFNS
from rdf.const import TYPE

RDF = RDFNS+u"RDF"
DESCRIPTION = RDFNS+u"Description"
ABOUT = RDFNS+u"about"
ID = RDFNS+u"ID"
RESOURCE = RDFNS+u"resource"

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
        name, atts = hack_around(name, atts)
            
        self.depth = self.depth + 1
        if name==RDF:
            RDFHandler(self.parser, self.adder, self)
            self.found_root = 1
        else:
            pass

    def end(self, name):
        name = join(split(name, '^'), '')
        self.depth = self.depth - 1
        if self.depth==0 and self.found_root==0:
            import sys
            sys.stderr.write(u"warning: Did not find a '%s' element\n" % RDF)
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
        name, atts = hack_around(name, atts)
        if name==DESCRIPTION:
            DescriptionHandler(self.parser, self.adder, self, atts)
        else:
            TypedNodeHandler(self.parser, self.adder, self, name, atts)

class IgnoreHandler(HandlerBase):
    def __init__(self, parser, adder, parent):
        HandlerBase.__init__(self, parser, adder, parent)

    def set_handlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        print "Ignoring '%s'" % name
        IgnoreHandler(self.parser, self.adder, self)

        
class DescriptionHandler(HandlerBase):
    def __init__(self, parser, adder, parent, atts):
        HandlerBase.__init__(self, parser, adder, parent)
        self.subject = None
        if atts.has_key(u"about"):
            self.subject = atts[u"about"]
        elif atts.has_key(u"ID"):
            self.subject = self.parser.GetBase() + u"#" + atts[u"ID"]
        elif atts.has_key(ABOUT):
            self.subject = atts[ABOUT]
        elif atts.has_key(ID):
            self.subject = self.parser.GetBase() + u"#" + atts[ID]
        else:
            import sys
            print atts
            sys.stderr.write(u"Descriptions must have either an about or an ID\n")
            
        for att in atts.keys():
            if att==u"about" or att==u"ID" or att==ABOUT or att==ID:
                pass
            else:
                self.adder(self.subject, att, literal(atts[att]))

    def set_handlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        name, atts = hack_around(name, atts)
        PropertyHandler(self.parser, self.adder, self, name, atts)
                        

class TypedNodeHandler(DescriptionHandler):
    def __init__(self, parser, adder, parent, name, atts):
        DescriptionHandler.__init__(self, parser, adder, parent, atts)
        self.adder(self.subject, TYPE, name)


class PropertyHandler(HandlerBase):
    def __init__(self, parser, adder, parent, name, atts):    
        HandlerBase.__init__(self, parser, adder, parent)
        self.predicate = name
        if atts.has_key(u"resource"):
            self.object = atts[u"resource"]
            if self.object[0]==u"#":
                self.object = self.parser.GetBase() + self.object
            for att in atts.keys():
                if att == u"resource":
                    pass
                else:
                    self.adder(self.object, att, literal(atts[att]))
        elif atts.has_key(RESOURCE):
            self.object = atts[RESOURCE]
            if self.object[0]==u"#":
                self.object = self.parser.GetBase() + self.object
            for att in atts.keys():
                if att == RESOURCE:
                    pass
                else:
                    self.adder(self.object, att, literal(atts[att]))
        else:
            self.object = literal(u"")

    def set_handlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        name, atts = hack_around(name, atts)
        if name==DESCRIPTION:
            self.object = atts[u"about"]
            DescriptionHandler(self.parser, self.adder, self, atts)
        else:
            IgnoreHandler(self.parser, self.adder, self)

    def char(self, data):
        self.object = self.object + data

    def end(self, name):
        name = join(split(name, '^'), '')
        self.adder(self.parent.subject, self.predicate, self.object)
        self.parent.set_handlers()

#~ $Log$
#~ Revision 8.1  2001/04/27 03:49:26  eikeon
#~ recoded to use namespace separator
#~
#~ Revision 8.0  2001/04/27 00:52:13  eikeon
#~ new release
