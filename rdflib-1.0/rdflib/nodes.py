
class URIRef(str):
    def n3(self):
        return "<%s>" % self

class Literal(str):
    def __add__(self, val):
        s = "".join([self,val])
        return Literal(s)
    
    def n3(self):
        return '"%s"' % self

class BNode(str):
    def __str__(self):
        return self.n3()
    
    def n3(self):
        return "_:a%s" % id(self)

def n3(value):
    if value[0] == '"' and value[-1] == '"':
        return Literal(value[1:-1])
    else:
        return URIRef(value[1:-1])

