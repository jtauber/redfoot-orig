
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


class Literal(str):
    def is_literal(self):
        return 1
