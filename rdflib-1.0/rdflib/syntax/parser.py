ns_separator = ""

from rdflib.nodes import URIRef, Literal, BNode
from rdflib.const import RDFNS, TYPE
from rdflib import exception

RDF = RDFNS + ns_separator + "RDF"
DESCRIPTION = RDFNS + ns_separator + "Description"
ABOUT = RDFNS + ns_separator + "about"
ABOUT_EACH = RDFNS + ns_separator + "aboutEach"
ABOUT_EACH_PREFIX = RDFNS + ns_separator + "aboutEachPrefix"
ID = RDFNS + ns_separator + "ID"
RESOURCE = RDFNS + ns_separator + "resource"

SEQ = RDFNS + ns_separator + "Seq"
BAG = RDFNS + ns_separator + "Bag"
ALT = RDFNS + ns_separator + "Alt"
LI = RDFNS + ns_separator + "li"
BAG_ID = RDFNS + ns_separator + "bagID"
PARSE_TYPE = RDFNS + ns_separator + "parseType"

def all_whitespace(data):
    for char in data:
        if char not in [chr(9),chr(10),chr(13),chr(32)]:
            return 0
    return 1

class DocumentHandler(object):
    def __init__(self, parser, add):
        self.parser = parser
        self.add = add
        #self.base = parser.GetBase()
        parser.StartElementHandler = self.child
        parser.CharacterDataHandler = self.char
        parser.EndElementHandler = self.end
        self.child_stack = [self.look_child,]
        self.char_stack = [self.default_char,]
        self.end_stack = [self.look_end,]
        self.subject_stack = []

    def set_base(self, base):
        self.__base = base
        
    def absolutize(self, uri):
        if uri == '' or uri[0] == "#":
            base = self.parser.GetBase()
            if base==None:
                return self.__base + uri
            return base + uri
        else:
            return uri

    def child(self, name, atts):
        self.child_stack[-1](name, atts)        

    def char(self, data):
        self.char_stack[-1](data)
    
    def end(self, name):
        self.end_stack[-1](name)

    def look_child(self, name, atts):
        if name == RDF:
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
        if name == DESCRIPTION:
            self.description(name, atts)
            self.child_stack.append(self.description_child)
            self.end_stack.append(self.description_end)                
        elif name == BAG:
            self.bag(name, atts)                        
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        elif name == ALT:
            self.alt(name, atts)                        
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        elif name == SEQ:
            self.sequence(name, atts)            
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        else:
            if name in [RDF, ID, ABOUT, BAG_ID, PARSE_TYPE, RESOURCE, LI,
                        ABOUT_EACH, ABOUT_EACH_PREFIX]:
                raise exception.ParserError("%s not allowed under rdf:RDF" % name)
            self.subject_stack.append(None)            
            self.typed_node(name, atts)
            self.add(self.subject_stack[-1], TYPE, URIRef(name))
            self.child_stack.append(self.description_child)
            self.end_stack.append(self.description_end)                


    def typed_node(self, name, atts):
        #self.subject = None
        if atts.has_key(ABOUT):
            self.subject_stack[-1] = URIRef(self.absolutize(atts[ABOUT]))
        elif atts.has_key(ID):
            self.subject_stack[-1] = URIRef(self.absolutize("#" + atts[ID]))
        else:
            self.subject_stack[-1] = BNode()

        for att in atts:
            if att in ["about", "aboutEach", "ID", "bagID",
                       "type", "resource", "parseType"]:
                raise exception.ParserError("%s requires an rdf: prefix" % att)
            if att in [LI, ABOUT_EACH_PREFIX]:                
                raise exception.ParserError("%s is forbidden as a property attribute name." % att)            
            if att == "about" or att == "ID" or \
                   att == ABOUT or att == ID:
                pass
            else:
                self.add(self.subject_stack[-1], URIRef(att), Literal(atts[att]))

    def description(self, name, atts):
        self.subject_stack.append(None)        
        self.typed_node(name, atts)
        #print "www:", self.subject_stack[-1], TYPE, URIRef(name)
        #self.add(self.subject_stack[-1], TYPE, URIRef(name))

    def description_child(self, name, atts):
        if name in [RDF, ID, ABOUT, BAG_ID, PARSE_TYPE, RESOURCE,
                    ABOUT_EACH, ABOUT_EACH_PREFIX]: # DESCRIPTION?, 
            raise exception.ParserError("%s is forbidden as a property element name." % name)
        self.li_count = 0        
        self.container_child(name, atts)

    def description_end(self, name):
        self.subject_stack.pop()
        self.child_stack.pop()
        self.end_stack.pop()

    def property(self, name, atts):
        self.predicate = URIRef(name)
        if atts.has_key(RESOURCE):
            if atts.has_key(PARSE_TYPE):
                if atts[PARSE_TYPE]=="Literal":
                    raise exception.ParserError("""specifying an rdf:parseType of "Literal" and an rdf:resource attribute at the same time is an error""")

            self.object = URIRef(self.absolutize(atts[RESOURCE]))
            for att in atts:
                if att == RESOURCE:
                    pass
                else:
                    #if len(att)>2 and att[0:3].lower()=='xml':
                    self.add(self.object, URIRef(att), Literal(atts[att]))
        else:
            for att in atts:
                if att == "resource":
                    raise exception.ParserError("%s not allowed here")
                if not att in [RESOURCE, PARSE_TYPE]:
                    #if len(att)>2 and att[0:3].lower()=='xml':
                    self.add(self.subject_stack[-1], URIRef(att), Literal(atts[att]))
            if PARSE_TYPE in atts:
                if atts[PARSE_TYPE]=="Literal":
                    self.object = Literal("")
                else:
                    self.object = BNode()
            else:
                self.object = Literal("")
        
    def property_child(self, name, atts):
        if name==SEQ:
            self.sequence(name, atts)                        
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        elif name==BAG:
            self.bag(name, atts)                                    
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        elif name==ALT:
            self.alt(name, atts)                                    
            self.child_stack.append(self.container_child)
            self.end_stack.append(self.default_end)
        else:
            if atts.has_key(ABOUT):
                self.object = URIRef(self.absolutize(atts[ABOUT]))
            elif atts.has_key(ID):
                self.object = URIRef(self.absolutize("#" + atts[ID]))
            else:
                self.object = BNode()

            if name==DESCRIPTION:
                self.description(name, atts)                
                self.child_stack.append(self.description_child)
                self.end_stack.append(self.description_end)                
            else:
                self.subject_stack.append(None)                
                self.typed_node(name, atts)
                self.add(self.subject_stack[-1], TYPE, URIRef(name))
                self.child_stack.append(self.description_child)
                self.end_stack.append(self.description_end)                

    def property_char(self, data):
        if not all_whitespace(data):
            if isinstance(self.object, Literal):
                self.object = self.object + data

    def property_end(self, name):
        self.add(self.subject_stack[-1], self.predicate, self.object)
        self.child_stack.pop()
        self.char_stack.pop()
        self.end_stack.pop()

    def container(self, name, atts):
        self.subject_stack.append(None)        
        self.typed_node(name, atts)
        self.object = self.subject_stack[-1] #??
        self.li_count = 0

    def container_child(self, name, atts):
        if name == LI:
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
        self.add(self.subject_stack[-1], TYPE, Literal(BAG))        

    def alt(self, name, atts):
        self.container(name, atts)
        ALT = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#Alt")
        self.add(self.subject_stack[-1], TYPE, Literal(ALT))        
        

    def sequence(self, name, atts):
        self.container(name, atts)
        SEQUENCE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq")
        self.add(self.subject_stack[-1], TYPE, SEQUENCE)        
        

    def li(self, name, atts):
        if atts.has_key("resource"):
            self.value = URIRef(self.absolutize(atts["resource"]))
        elif atts.has_key(RESOURCE):
            self.value = URIRef(self.absolutize(atts[RESOURCE]))
        else:
            self.value = Literal("")

    def li_child(self, name, atts):
        raise exception.RDFSeqChildNotAllowedError()

    def li_char(self, data):
        if not all_whitespace(data):
            if not isinstance(self.value, Literal):
                raise exception.ResourceAndCharContentError(self.subject_stack[-1])
            self.value = self.value + data

    def li_end(self, name):
        self.li_count = self.li_count + 1
        predicate = URIRef(RDFNS + "_" + str(self.li_count))
        self.add(self.subject_stack[-1], predicate, self.value)
        self.child_stack.pop()
        self.char_stack.pop()
        self.end_stack.pop()


class Parser(object):
    def __init__(self):
        super(Parser, self).__init__()

    def parse(self, file, baseURI):
        from xml.parsers.expat import ParserCreate        
        parser = ParserCreate(namespace_separator=ns_separator)
        parser.returns_unicode = 0
        dh = DocumentHandler(parser, self.add)
        dh.set_base(baseURI)        
        parser.ParseFile(file)
        file.close()

    def parse_URI(self, location, baseURI=None):
        baseURI = baseURI or location
        from urllib import urlopen
        file = urlopen(location)
        self.parse(file, baseURI)
        
