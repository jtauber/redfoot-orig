from redfoot.rdf.store.urigen import generate_uri
from string import join, split

ANON = "http://redfoot.sourceforge.net/2001/08/ANON/"

#TODO flag for where RDF can be assumed
#TODO proper handling of relative URIs

ns_separator = "^"

def parse(adder, file, baseURI):
    import xml.parsers.expat

    parser = xml.parsers.expat.ParserCreate(namespace_separator=ns_separator)
    parser.SetBase(baseURI)
    parser.returns_unicode = 0
    
    LookForRDFHandler(parser, adder, None)

    parser.ParseFile(file)
        
    file.close()

    
#  def parse_URI(adder, location, baseURI=None):
#      baseURI = baseURI or location

#      from urllib import urlopen
#      file = urlopen(location)

#      parse(adder, file, baseURI)

    
# TODO: do we still want the level of isolation where the parser /
# serializer do not know about the objects? If so, we will have to
# change this... as TYPE is now an object.
from redfoot.rdf.const import RDFNS, TYPE

RDF_ELEMENT = RDFNS + ns_separator + "RDF"
DESCRIPTION_ELEMENT = RDFNS + ns_separator + "Description"
ABOUT_ATTRIBUTE = RDFNS + ns_separator + "about"
ID_ATTRIBUTE = RDFNS + ns_separator + "ID"
RESOURCE_ATTRIBUTE = RDFNS + ns_separator + "resource"

SEQ_ELEMENT = RDFNS + ns_separator + "Seq"
BAG_ELEMENT = RDFNS + ns_separator + "Bag"
ALT_ELEMENT = RDFNS + ns_separator + "Alt"
LI_ELEMENT = RDFNS + ns_separator + "li"

class HandlerBase:
    def __init__(self, parser, adder, parent):
        self.parser = parser
        self.adder = adder
        self.parent = parent
        self.set_handlers()

    def set_handlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def char(self, data):
        pass

    def child(self, name, atts):
        pass
    
    def end(self, name):
        self.parent.set_handlers()

    
class LookForRDFHandler(HandlerBase):
    def __init__(self, parser, adder, parent):
        HandlerBase.__init__(self, parser, adder, parent)

    def child(self, name, atts):
        if name == RDF_ELEMENT:
            RDFHandler(self.parser, self.adder, self)
        else:
            LookForRDFHandler(self.parser, self.adder, self)


class RDFHandler(HandlerBase):
    def __init__(self, parser, adder, parent):
        HandlerBase.__init__(self, parser, adder, parent)

    def child(self, name, atts):
        if name == DESCRIPTION_ELEMENT:
            DescriptionHandler(self.parser, self.adder, self, atts)
        elif name == BAG_ELEMENT:
            BagHandler(self.parser, self.adder, self, name, atts)
        elif name == ALT_ELEMENT:
            AltHandler(self.parser, self.adder, self, name, atts)
        elif name == SEQ_ELEMENT:
            SeqHandler(self.parser, self.adder, self, name, atts)
        else:
            TypedNodeHandler(self.parser, self.adder, self, name, atts)


class DescriptionHandler(HandlerBase):
    def __init__(self, parser, adder, parent, atts):
        HandlerBase.__init__(self, parser, adder, parent)
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

        if self.subject[0] == "#": # TODO do this elsewhere too
            self.subject = self.parser.GetBase() + self.subject

        for att in atts.keys():
            if att == "about" or att == "ID" or \
               att == ABOUT_ATTRIBUTE or att == ID_ATTRIBUTE:
                pass
            else:
                new_att = join(split(att, "^"), "")
                self.adder(self.subject, new_att, atts[att],
                           anonymous_subject=self.anonymous, literal_object=1)

    def child(self, name, atts):
        PropertyHandler(self.parser, self.adder, self, name, atts)
                        

class TypedNodeHandler(DescriptionHandler):
    def __init__(self, parser, adder, parent, name, atts):
        DescriptionHandler.__init__(self, parser, adder, parent, atts)
        type = join(split(name, "^"), "")
        self.adder(self.subject, str(TYPE), type, anonymous_subject=self.anonymous)


def all_whitespace(data):
    for char in data:
        if char not in [chr(9),chr(10),chr(13),chr(32)]:
            return 0
    return 1


class ContainerHandler(TypedNodeHandler):
    def __init__(self, parser, adder, parent, name, atts):
        TypedNodeHandler.__init__(self, parser, adder, parent, name, atts)
        parent.object = self.subject
        parent.anonymous_object = self.anonymous
        self.li_count = 0

    def child(self, name, atts):
        if name == LI_ELEMENT:
            LIHandler(self.parser, self.adder, self, atts)
        else:
            PropertyHandler(self.parser, self.adder, self, name, atts)

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
    def __init__(self, parser, adder, parent, atts):
        HandlerBase.__init__(self, parser, adder, parent)
        self.literal = 0
        if atts.has_key("resource"):
            self.value = atts["resource"]
            if self.value[0] == "#":
                self.value = self.parser.GetBase() + self.value
        elif atts.has_key(RESOURCE_ATTRIBUTE):
            self.value = atts[RESOURCE_ATTRIBUTE]
            if self.value[0] == "#":
                self.value = self.parser.GetBase() + self.value
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
    def __init__(self, parser, adder, parent, name, atts):
        HandlerBase.__init__(self, parser, adder, parent)
        self.predicate = join(split(name, "^"), "")
        self.literal = 0
        self.anonymous_object = 0
        if atts.has_key("resource"):
            self.object = atts["resource"]
            if self.object[0] == "#":
                self.object = self.parser.GetBase() + self.object
            for att in atts.keys():
                if att == "resource":
                    pass
                else:
                    new_att = join(split(att, "^"), "")
                    self.adder(self.object, new_att, atts[att],
                               literal_object=1)
        elif atts.has_key(RESOURCE_ATTRIBUTE):
            self.object = atts[RESOURCE_ATTRIBUTE]
            if self.object[0] == "#":
                self.object = self.parser.GetBase() + self.object
            for att in atts.keys():
                if att == RESOURCE_ATTRIBUTE:
                    pass
                else:
                    new_att = join(split(att, "^"), "")
                    self.adder(self.object, new_att,atts[att],
                               literal_object=1)
        else:
            self.object = ""
            self.literal = 1

    def child(self, name, atts):
        self.literal = 0
        if name==SEQ_ELEMENT:
            SeqHandler(self.parser, self.adder, self, name, atts)
        elif name==BAG_ELEMENT:
            BagHandler(self.parser, self.adder, self, name, atts)
        elif name==ALT_ELEMENT:
            AltHandler(self.parser, self.adder, self, name, atts)
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
                raise "Descriptions must have either an about or an ID"
            if name==DESCRIPTION_ELEMENT:
                DescriptionHandler(self.parser, self.adder, self, atts)
            else:
                TypedNodeHandler(self.parser, self.adder, self, name, atts)

    def char(self, data):
        if not all_whitespace(data):
            if not self.literal:
                raise "has both character content and a resource attribute"
            self.object = self.object + data

    def end(self, name):
        self.adder(self.parent.subject, self.predicate, self.object,
                   literal_object=self.literal, anonymous_object=self.anonymous_object)
        HandlerBase.end(self, name)




from redfoot.rdf.objects import resource, literal

class Parser:

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
        
