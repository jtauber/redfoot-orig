import pyexpat

rdfns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

class rootHandler:
    def __init__(self, parser, adder, parent):
        self.parser = parser
        self.adder = adder
        self.parent = parent
        self.parser.StartElementHandler = self.child
        
    def child(self, name, atts):
        if name==rdfns+"RDF":
            RDFHandler(self.parser, self.adder, self)
        else:
            pass

    def resume(self):
        pass

class RDFHandler:
    def __init__(self, parser, adder, parent):
        self.parser = parser
        self.adder = adder
        self.parent = parent
        self.resume()

    def resume(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        if name==rdfns+"Description":
            DescriptionHandler(self.parser, self.adder, self, atts)
        else:
            TypedNodeHandler(self.parser, self.adder, self, name, atts)
        
    def char(self, data):
        pass

    def end(self, name):
        self.parent.resume()

class DescriptionHandler:
    def __init__(self, parser, adder, parent, atts):
        self.parser = parser
        self.adder = adder
        self.parent = parent
        self.subject = None
        if atts.has_key("about"):
            self.subject = atts["about"]
        elif atts.has_key("ID"):
            self.subject = self.parser.GetBase() + "#" + atts["ID"]
        elif atts.has_key(rdfns+"about"):
            self.subject = atts[rdfns+"about"]
        elif atts.has_key(rdfns+"ID"):
            self.subject = self.parser.GetBase() + "#" + atts[rdfns+"ID"]
        for att in atts.keys():
            if att=="about" or att=="ID" or att==rdfns+"about" or att==rdfns+"ID":
                pass
            else:
                self.adder(self.subject, att, "^"+atts[att])
        self.resume()

    def resume(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        PropertyHandler(self.parser, self.adder, self, name, atts)
                        
    def char(self, data):
        pass

    def end(self, name):
        self.parent.resume()

class TypedNodeHandler(DescriptionHandler):
    def __init__(self, parser, adder, parent, name, atts):
        DescriptionHandler.__init__(self, parser, adder, parent, atts)
        self.adder(self.subject, rdfns+"type", name)

class PropertyHandler:
    def __init__(self, parser, adder, parent, name, atts):    
        self.parser = parser
        self.adder = adder
        self.parent = parent
        self.predicate = name
        if atts.has_key("resource"):
            self.object = atts["resource"]
            for att in atts.keys():
                if att == "resource":
                    pass
                else:
                    self.adder(self.object, att, "^"+atts[att])
        elif atts.has_key(rdfns+"resource"):
            self.object = atts[rdfns+"resource"]
            for att in atts.keys():
                if att == rdfns+"resource":
                    pass
                else:
                    self.adder(self.object, att, "^"+atts[att])
        else:
            self.object = "^"
        self.resume()

    def resume(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def child(self, name, atts):
        if name==rdfns+"Description":
            self.object = atts["about"]
            DescriptionHandler(self.parser, self.adder, self, atts)
        else:
            pass

    def char(self, data):
        self.object = self.object + data

    def end(self, name):
        self.adder(self.parent.subject, self.predicate, self.object)
        self.parent.resume()
