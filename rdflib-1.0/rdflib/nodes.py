
class URIRef(str):
    def n3(self):
        return "<%s>" % self

class Literal(str):
    def __add__(self, val):
        s = "".join([self,val])
        return Literal(s)
    
    def n3(self):
        return '"%s"' % self

node_id = 0
class BNode(str):
    def __new__(cls):
        global node_id
        node_id += 1
        value = "_:a%s" % node_id
        return str.__new__(cls, value)
        
    def n3(self):
        return str(self)

def n3(value):
    if value[0] == '"' and value[-1] == '"':
        return Literal(value[1:-1])
    else:
        return URIRef(value[1:-1])

