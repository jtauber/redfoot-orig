ns_separator = ""

from rdflib.nodes import URIRef, Literal, BNode
from rdflib.const import RDFNS, TYPE
from rdflib import exception

RDF_ELEMENT = RDFNS + ns_separator + "RDF"
DESCRIPTION_ELEMENT = RDFNS + ns_separator + "Description"
ABOUT_ATTRIBUTE = RDFNS + ns_separator + "about"
ID_ATTRIBUTE = RDFNS + ns_separator + "ID"
RESOURCE_ATTRIBUTE = RDFNS + ns_separator + "resource"

SEQ_ELEMENT = RDFNS + ns_separator + "Seq"
BAG_ELEMENT = RDFNS + ns_separator + "Bag"
ALT_ELEMENT = RDFNS + ns_separator + "Alt"
LI_ELEMENT = RDFNS + ns_separator + "li"

def all_whitespace(data):
    for char in data:
        if char not in [chr(9),chr(10),chr(13),chr(32)]:
            return 0
    return 1

class DocumentHandler(object):
    def __init__(self, parser, add):
        self.parser = parser
        self.add = add
        self.base = parser.GetBase()
        parser.StartElementHandler = self.child
        parser.CharacterDataHandler = self.char
        parser.EndElementHandler = self.end
        self.child_stack = [self.look_child,]
        self.char_stack = [self.default_char,]
        self.end_stack = [self.look_end,]

    def absolutize(self, uri):
        if uri == '' or uri[0] == "#":
            return self.base + uri
        else:
            return uri

    def child(self, name, atts):
        self.child_stack[-1](name, atts)        

    def char(self, data):
        self.char_stack[-1](data)
    
    def end(self, name):
        self.end_stack[-1](name)

    def look_child(self, name, atts):
        if name == RDF_ELEMENT:
            self.child_stack.append(self.rdf_child)            

    def look_end(self, name):
        pass # Keep looking

    def default_child(self, name, atts):
        self.child_stack.append(self.default_child)
        self.end_stack.append(self.default_end)        

    def default_char(self, data):
        pass

    def default_end(self, name):
        self.child_stack.pop()
        self.end_stack.pop()

    def rdf_child(self, name, atts):
        if name == DESCRIPTION_ELEMENT:
            self.description(name, atts)            
            self.child_stack.append(self.description_child)
            self.end_stack.append(self.default_end)                
        elif name == BAG_ELEMENT:
            self.bag(name, atts)                        
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        elif name == ALT_ELEMENT:
            self.alt(name, atts)                        
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        elif name == SEQ_ELEMENT:
            self.sequence(name, atts)            
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        else:
            self.typed_node(name, atts)
            self.add(self.subject, TYPE, URIRef(name))                    
            self.child_stack.append(self.description_child)
            self.end_stack.append(self.default_end)                


    def typed_node(self, name, atts):
        self.subject = None
        if atts.has_key("about"):
            self.subject = URIRef(self.absolutize(atts["about"]))
        elif atts.has_key("ID"):
            self.subject = URIRef(self.base + "#" + atts["ID"])
        elif atts.has_key(ABOUT_ATTRIBUTE):
            self.subject = URIRef(self.absolutize(atts[ABOUT_ATTRIBUTE]))
        elif atts.has_key(ID_ATTRIBUTE):
            self.subject = URIRef(self.base + "#" + atts[ID_ATTRIBUTE])
        else:
            self.subject = BNode()

        for att in atts.keys():
            if att == "about" or att == "ID" or \
                   att == ABOUT_ATTRIBUTE or att == ID_ATTRIBUTE:
                pass
            else:
                self.add(self.subject, URIRef(att), Literal(atts[att]))

    def description(self, name, atts):
        self.typed_node(name, atts)
        self.add(self.subject, TYPE, URIRef(name))

    def description_child(self, name, atts):
        self.li_count = 0        
        self.container_child(name, atts)

    def property(self, name, atts):
        self.predicate = URIRef(name)
        if atts.has_key("resource"):
            self.object = URIRef(self.absolutize(atts["resource"]))
            for att in atts.keys():
                if att == "resource":
                    pass
                else:
                    if len(att)>2 and att[0:3].lower()=='xml': 
                        self.add(self.object, URIRef(att), Literal(atts[att]))
        elif atts.has_key(RESOURCE_ATTRIBUTE):
            self.object = URIRef(self.absolutize(atts[RESOURCE_ATTRIBUTE]))
            for att in atts.keys():
                if att == RESOURCE_ATTRIBUTE:
                    pass
                else:
                    if len(att)>2 and att[0:3].lower()=='xml':
                        self.add(self.object, URIRef(att), Literal(atts[att]))
        else:
            for att in atts:
                if att != "resource" and att != RESOURCE_ATTRIBUTE:
                    if len(att)>2 and att[0:3].lower()=='xml':
                        self.add(self.subject, URIRef(att), Literal(atts[att]))
            self.object = Literal("")
        
    def property_child(self, name, atts):
        if name==SEQ_ELEMENT:
            self.sequence(name, atts)                        
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        elif name==BAG_ELEMENT:
            self.bag(name, atts)                                    
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        elif name==ALT_ELEMENT:
            self.alt(name, atts)                                    
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        else:
            if atts.has_key("about"):
                self.object = URIRef(self.absolutize(atts["about"]))
            elif atts.has_key("ID"):
                self.object = URIRef(self.uri + "#" + atts["ID"])
            elif atts.has_key(ABOUT_ATTRIBUTE):
                self.object = URIRef(self.absolutize(atts[ABOUT_ATTRIBUTE]))
            elif atts.has_key(ID_ATTRIBUTE):
                self.object = URIRef(self.uri + "#" + atts[ID_ATTRIBUTE])
            else:
                self.object = BNode()
                #raise exception.MalformedDescriptionError(name)
            if name==DESCRIPTION_ELEMENT:
                self.description(name, atts)                
                self.child_stack.append(self.description_child)
                self.end_stack.append(self.default_end)                
            else:
                self.typed_node(name, atts)                
                self.child_stack.append(self.description_child)
                self.end_stack.append(self.default_end)                

    def property_char(self, data):
        if not all_whitespace(data):
            if not isinstance(self.object, Literal):
                raise exception.ResourceAndCharContentError(self.subject)
            self.object = self.object + data

    def property_end(self, name):
        self.add(self.subject, self.predicate, self.object)
        self.child_stack.pop()
        self.char_stack.pop()
        self.end_stack.pop()

    def container(self, name, atts):
        self.typed_node(name, atts)
        self.object = self.subject
        self.li_count = 0

    def container_child(self, name, atts):
        if name == LI_ELEMENT:
            self.li(name, atts)            
            self.child_stack.append(self.li_child)
            self.char_stack.append(self.li_char)
            self.end_stack.append(self.li_end)
        else:
            self.property(name, atts)            
            self.child_stack.append(self.property_child)
            self.char_stack.append(self.property_char)
            self.end_stack.append(self.property_end)                        

    def bag(self, name, atts):
        self.container(name, atts)
        BAG = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag")
        self.add(self.subject, TYPE, Literal(BAG))        

    def alt(self, name, atts):
        self.container(name, atts)
        ALT = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#Alt")
        self.add(self.subject, TYPE, Literal(ALT))        
        

    def sequence(self, name, atts):
        self.container(name, atts)
        SEQUENCE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#Sequence")
        self.add(self.subject, TYPE, Literal(SEQUENCE))        
        

    def li(self, name, atts):
        if atts.has_key("resource"):
            self.value = URIRef(self.absolutize(atts["resource"]))
        elif atts.has_key(RESOURCE_ATTRIBUTE):
            self.value = URIRef(self.uri + atts[RESOURCE_ATTRIBUTE])
        else:
            self.value = Literal("")

    def li_child(self, name, atts):
        raise exception.RDFSeqChildNotAllowedError()

    def li_char(self, data):
        if not all_whitespace(data):
            if not isinstance(self.value, Literal):
                raise exception.ResourceAndCharContentError(self.subject)
            self.value = self.value + data

    def li_end(self, name):
        self.li_count = self.li_count + 1
        predicate = URIRef(RDFNS + "_" + str(self.li_count))
        self.add(self.subject, predicate, self.value)
        self.child_stack.pop()
        self.char_stack.pop()
        self.end_stack.pop()


class Parser(object):
    def __init__(self):
        super(Parser, self).__init__()

    def parse(self, file, baseURI):
        from xml.parsers.expat import ParserCreate        
        parser = ParserCreate(namespace_separator=ns_separator)
        parser.SetBase(baseURI)
        parser.returns_unicode = 0
        DocumentHandler(parser, self.add)
        parser.ParseFile(file)
        file.close()

    def parse_URI(self, location, baseURI=None):
        baseURI = baseURI or location
        from urllib import urlopen
        file = urlopen(location)
        self.parse(file, baseURI)
        
