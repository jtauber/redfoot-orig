ns_separator = ""

from rdflib.nodes import URIRef, Literal, BNode
from rdflib.const import RDFNS, TYPE
from rdflib import exception

def uriref(v):
    if v[0]=="<" and v[-1]==">":
        return URIRef(v[1:-1])
    else:
        raise exception.ParserError("NTParser error: invalid uriref of '%s'" % v)

bNodes = {}
def node_id(v):
    if v[0:2]=="_:":
        name = v[3:]
        if not name in bNodes:
            bNodes[name] = BNode()
        return bNodes[name]
    else:
        raise exception.ParserError("NTParser error: invalid node_id of '%s'" % v)

def literal(v):
    if v[0]=='"':
        if v[-1]=='"':
            return lang_string(v)
    elif v[0:3]=="xml":
        return lang_string(v[3:])
    else:
        raise exception.ParserError("NTParser error: invalid literal of '%s'" % v)

def lang_string(v):
    if v[0]=='"':    
        return Literal(v[1:-1])
    else:
        raise exception.NotYetImplemented()

class NTParser(object):
    def __init__(self):
        super(NTParser, self).__init__()

    def parse_nt(self, file, baseURI):
        for line in iter(file.readline, ""):
            line = line.lstrip()
            if line and not line[0]=="#": 
                s, p, o = line.split(None, 2)
                o = o.rstrip()
                if not o[-1]==".":
                    raise exception.ParserError("""NTParser error: triple is missing "." """)
                o = o[:-1]
                o = o.rstrip()
                
                if s[0]=="<":
                    s = uriref(s)
                elif s[0]=="_":
                    s = node_id(s)
                else:
                    raise exception.ParserError("NTParser error: unexpected subject of '%s'" % s)
                if p[0]=="<":
                    p = uriref(p)
                else:
                    raise exception.ParserError("NTParser error: unexpected predicate of '%s'" % p)
                if o[0]=="<":
                    o = uriref(o)
                elif o[0]=="_":
                    o = node_id(o)
                else:
                    o = literal(o)
                self.add(s, p, o)
            
        file.close()

    def parse_nt_URI(self, location, baseURI=None):
        baseURI = baseURI or location
        from urllib import urlopen
        file = urlopen(location)
        self.parse_nt(file, baseURI)
        
