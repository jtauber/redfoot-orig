
resources_dict = {}
literal_dict = {}

def resource(uri, anonymous=None):
    if uri==None:
        r = None
    elif resources_dict.has_key(uri):
        r = resources_dict[uri]
    else:
        r = resources_dict[uri] = Resource(uri, anonymous)
    return r

def literal(value):
    if value==None:
        r = None
    elif literal_dict.has_key(value):
        r = literal_dict[value]
    else:
        r = literal_dict[value] = Literal(value)
    return r


class Resource:
    def __init__(self, uri, anonymous):
        self.uri = uri
        self.anonymous = anonymous

    def __str__(self):
        return self.uri

    def is_literal(self):
        return None

    def isAnonymous(self):
        return self.anonymous


class Literal:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def is_literal(self):
        return 1
