
from redfootlib.xml.handler import HandlerBase as AbstractHandlerBase

class HandlerBase(AbstractHandlerBase):

    def __init__(self, parser, parent, adder):
        AbstractHandlerBase.__init__(self, parser, parent)
        self.adder = adder

from redfootlib.rdf.store.urigen import generate_uri


ANON = "http://redfoot.sourceforge.net/2001/08/ANON/"

#TODO flag for where RDF can be assumed
#TODO proper handling of relative URIs

ns_separator = ""

def parse(adder, file, baseURI):
    import xml.parsers.expat

    parser = xml.parsers.expat.ParserCreate(namespace_separator=ns_separator)
    parser.SetBase(baseURI)
    parser.returns_unicode = 0
    
    LookForRDFHandler(parser, None, adder)

    parser.ParseFile(file)
        
    file.close()

    
# TODO: do we still want the level of isolation where the parser /
# serializer do not know about the objects? If so, we will have to
# change this... as TYPE is now an object.
from redfootlib.rdf.const import RDFNS, TYPE

RDF_ELEMENT = RDFNS + ns_separator + "RDF"
DESCRIPTION_ELEMENT = RDFNS + ns_separator + "Description"
ABOUT_ATTRIBUTE = RDFNS + ns_separator + "about"
ID_ATTRIBUTE = RDFNS + ns_separator + "ID"
RESOURCE_ATTRIBUTE = RDFNS + ns_separator + "resource"

SEQ_ELEMENT = RDFNS + ns_separator + "Seq"
BAG_ELEMENT = RDFNS + ns_separator + "Bag"
ALT_ELEMENT = RDFNS + ns_separator + "Alt"
LI_ELEMENT = RDFNS + ns_separator + "li"


class LookForRDFHandler(HandlerBase):
    def __init__(self, parser, parent, adder):
        HandlerBase.__init__(self, parser, parent, adder)

    def child(self, name, atts):
        if name == RDF_ELEMENT:
            RDFHandler(self.parser, self, self.adder)
        else:
            LookForRDFHandler(self.parser, self, self.adder)


class RDFHandler(HandlerBase):
    def __init__(self, parser, parent, adder):
        HandlerBase.__init__(self, parser, parent, adder)

    def child(self, name, atts):
        if name == DESCRIPTION_ELEMENT:
            DescriptionHandler(self.parser, self, self.adder, atts)
        elif name == BAG_ELEMENT:
            BagHandler(self.parser, self, self.adder, name, atts)
        elif name == ALT_ELEMENT:
            AltHandler(self.parser, self, self.adder, name, atts)
        elif name == SEQ_ELEMENT:
            SeqHandler(self.parser, self, self.adder, name, atts)
        else:
            TypedNodeHandler(self.parser, self, self.adder, name, atts)


def absolutize(base, uri):
    if uri == '' or uri[0] == "#":
        return base + uri
    else:
        return uri



class DescriptionHandler(HandlerBase):
    def __init__(self, parser, parent, adder, atts):
        HandlerBase.__init__(self, parser, parent, adder)
        self.subject = None
        self.anonymous = 0
        if atts.has_key("about"):
            self.subject = atts["about"]
        elif atts.has_key("ID"):
            self.subject = "#" + atts["ID"]
        elif atts.has_key(ABOUT_ATTRIBUTE):
            self.subject = atts[ABOUT_ATTRIBUTE]
        elif atts.has_key(ID_ATTRIBUTE):
            self.subject = "#" + atts[ID_ATTRIBUTE]
        else:
            self.subject = ANON + generate_uri()
            self.anonymous = 1

        self.subject = absolutize(self.parser.GetBase(), self.subject)

        for att in atts.keys():
            if att == "about" or att == "ID" or \
               att == ABOUT_ATTRIBUTE or att == ID_ATTRIBUTE:
                pass
            else:
                self.adder(self.subject, att, atts[att],
                           anonymous_subject=self.anonymous, literal_object=1)

    def child(self, name, atts):
        PropertyHandler(self.parser, self, self.adder, name, atts)
                        

class TypedNodeHandler(DescriptionHandler):
    def __init__(self, parser, parent, adder, name, atts):
        DescriptionHandler.__init__(self, parser, parent, adder, atts)
        type = name
        adder(self.subject, str(TYPE), type, anonymous_subject=self.anonymous)


def all_whitespace(data):
    for char in data:
        if char not in [chr(9),chr(10),chr(13),chr(32)]:
            return 0
    return 1


class ContainerHandler(TypedNodeHandler):
    def __init__(self, parser, parent, adder, name, atts):
        TypedNodeHandler.__init__(self, parser, parent, adder, name, atts)
        parent.object = self.subject
        parent.anonymous_object = self.anonymous
        self.li_count = 0

    def child(self, name, atts):
        if name == LI_ELEMENT:
            LIHandler(self.parser, self, self.adder, atts)
        else:
            PropertyHandler(self.parser, self, self.adder, name, atts)

    def add_li(self, value, literal):
        self.li_count = self.li_count + 1
        predicate = RDFNS + "_" + str(self.li_count)
        self.adder(self.subject, predicate, value, literal_object=literal, anonymous_subject=self.anonymous)


class BagHandler(ContainerHandler):
    pass


class AltHandler(ContainerHandler):
    pass


class SeqHandler(ContainerHandler):
    pass


class LIHandler(HandlerBase):
    def __init__(self, parser, parent, adder, atts):
        HandlerBase.__init__(self, parser, parent, adder)
        self.literal = 0
        if atts.has_key("resource"):
            self.value = atts["resource"]
            self.value = absolutize(self.parser.GetBase(), self.value)                
        elif atts.has_key(RESOURCE_ATTRIBUTE):
            self.value = atts[RESOURCE_ATTRIBUTE]
            self.value = absolutize(self.parser.GetBase(), self.value)
        else:
            self.value = ""
            self.literal = 1
            
    def char(self, data):
        if not all_whitespace(data):
            if not self.literal:
                raise "has both character content and a resource attribute"
            self.value = self.value + data

    def end(self, name):
        self.parent.add_li(self.value, self.literal)
        HandlerBase.end(self, name)


class PropertyHandler(HandlerBase):
    def __init__(self, parser, parent, adder, name, atts):
        HandlerBase.__init__(self, parser, parent, adder)
        self.predicate = name
        self.literal = 0
        self.anonymous_object = 0
        if atts.has_key("resource"):
            self.object = atts["resource"]
            self.object = absolutize(self.parser.GetBase(), self.object)                                                
            for att in atts.keys():
                if att == "resource":
                    pass
                else:
                    self.adder(self.object, att, atts[att],
                               literal_object=1)
        elif atts.has_key(RESOURCE_ATTRIBUTE):
            self.object = atts[RESOURCE_ATTRIBUTE]
            self.object = absolutize(self.parser.GetBase(), self.object)
            for att in atts.keys():
                if att == RESOURCE_ATTRIBUTE:
                    pass
                else:
                    self.adder(self.object, att,atts[att],
                               literal_object=1)
        else:
            self.object = ""
            self.literal = 1

    def child(self, name, atts):
        self.literal = 0
        if name==SEQ_ELEMENT:
            SeqHandler(self.parser, self, self.adder, name, atts)
        elif name==BAG_ELEMENT:
            BagHandler(self.parser, self, self.adder, name, atts)
        elif name==ALT_ELEMENT:
            AltHandler(self.parser, self, self.adder, name, atts)
        else:
            if atts.has_key("about"):
                self.object = atts["about"]
            elif atts.has_key("ID"):
                self.object = self.parser.GetBase() + "#" + atts["ID"]
            elif atts.has_key(ABOUT_ATTRIBUTE):
                self.object = atts[ABOUT_ATTRIBUTE]
            elif atts.has_key(ID_ATTRIBUTE):
                self.object = self.parser.GetBase() + "#" + atts[ID_ATTRIBUTE]
            else:
                print "Descriptions must have either an about or an ID '%s'" % name
            if name==DESCRIPTION_ELEMENT:
                DescriptionHandler(self.parser, self, self.adder, atts)
            else:
                TypedNodeHandler(self.parser, self, self.adder, name, atts)

    def char(self, data):
        if not all_whitespace(data):
            if not self.literal:
                raise "has both character content and a resource attribute"
            self.object = self.object + data
        else:
            if self.literal:
                self.object = self.object + data

    def end(self, name):
        self.adder(self.parent.subject, self.predicate, self.object,
                   literal_object=self.literal, anonymous_object=self.anonymous_object)
        HandlerBase.end(self, name)




from redfootlib.rdf.objects import resource, literal

class Parser(object):
    def __init__(self):
        super(Parser, self).__init__()

    def add_statement(self, subject, predicate, object, literal_object=None, anonymous_subject=None, anonymous_object=None):
        s = resource(subject, anonymous_subject)
        p = resource(predicate)
        if literal_object:
            o = literal(object)
        else:
            o = resource(object, anonymous_object)
        self.add(s, p, o)

    def parse(self, file, baseURI):
        parse(self.add_statement, file, baseURI)

    def parse_URI(self, location, baseURI=None):
        baseURI = baseURI or location
        
        from urllib import urlopen
        file = urlopen(location)
        
        self.parse(file, baseURI)
        
