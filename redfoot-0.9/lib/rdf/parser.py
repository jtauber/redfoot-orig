# $Header$

def parseRDF(adder, location, baseURI=None):
    if baseURI==None:
        baseURI = location

    import pyexpat
    parser = pyexpat.ParserCreate(namespace_separator="")

    parser.SetBase(baseURI)
    RootHandler(parser, adder, None)

    from urllib import urlopen
    f = urlopen(location)
    parser.ParseFile(f)
    f.close()

rdfns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

from rdf.literal import literal, is_literal

class RootHandler:
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
                self.adder(self.subject, att, literal(atts[att]))
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
            if self.object[0]=="#":
                self.object = self.parser.GetBase() + self.object
            for att in atts.keys():
                if att == "resource":
                    pass
                else:
                    self.adder(self.object, att, literal(atts[att]))
        elif atts.has_key(rdfns+"resource"):
            self.object = atts[rdfns+"resource"]
            if self.object[0]=="#":
                self.object = self.parser.GetBase() + self.object
            for att in atts.keys():
                if att == rdfns+"resource":
                    pass
                else:
                    self.adder(self.object, att, literal(atts[att]))
        else:
            self.object = literal("")
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

#~ $Log$
#~ Revision 4.3  2000/12/03 22:12:12  jtauber
#~ changed class RDFParser to function parseRDF
#~
#~ Revision 4.2  2000/12/03 22:07:14  jtauber
#~ put literal handling code in store.py
#~
#~ Revision 4.1  2000/12/03 19:36:45  jtauber
#~ moved ^ trick to functions
#~
#~ Revision 4.0  2000/11/06 15:57:33  eikeon
#~ VERSION 4.0
#~
#~ Revision 3.1  2000/11/02 21:48:27  eikeon
#~ removed old log messages
#~
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
