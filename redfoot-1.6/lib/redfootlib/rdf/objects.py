
def resource(uri, anonymous=None):
    return URIRef(uri)

def literal(value):
    return Literal(value)

#----------------------

class URIRef(str):
    def n3(self):
        return "<%s>" % str(self)

class Literal(str):
    def n3(self):
        return '"%s"' % str(self)

class BNode(str):
    def n3(self):
        return "_:a%s" % id(self)

def n3(value):
    if value[0] == '"' and value[-1] == '"':
        return Literal(value[1:-1])
    else:
        return URI(value[1:-1])

