
def resource(uri, anonymous=None):
    if uri==None:
        return None
    elif anonymous:
        r = AnonymousResource(uri)
    else:
        r = Resource(uri)
    return r

def literal(value):
    if value==None:
        return None
    else:
        return Literal(value)

def n3(value):
    if value[0] == '"' and value[-1] == '"':
        return literal(value[1:-1])
    else:
        return resource(value[1:-1])
    

class AnonymousResource(str):
    def is_literal(self):
        return None

    def isAnonymous(self):
        return 1
    
class Resource(str):
    def is_literal(self):
        return None

    def isAnonymous(self):
        return None

    def n3(self):
        return "<%s>" % str(self)


class Literal(str):
    def is_literal(self):
        return 1

    def n3(self):
        return '"%s"' % str(self)
    
