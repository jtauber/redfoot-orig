
resources_dict = {}
literal_dict = {}

def resource(uri, anonymous=None):
    if uri:
        uri = intern(uri)
    if uri==None:
        r = None
    elif resources_dict.has_key(uri):
        r = resources_dict[uri]
    else:
        if anonymous:
            r = resources_dict[uri] = AnonymousResource(uri)
            r.uri = uri
        else:
            r = resources_dict[uri] = Resource(uri)
            r.uri = uri

    return r

def literal(value):
    if value:
        value = intern(value)
    if value==None:
        r = None
    elif literal_dict.has_key(value):
        r = literal_dict[value]
    else:
        r = literal_dict[value] = Literal(value)
    return r


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
