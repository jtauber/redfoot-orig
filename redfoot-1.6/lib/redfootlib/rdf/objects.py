from rdflib.nodes import URIRef, Literal

def resource(uri, anonymous=None):
    return URIRef(uri)


def literal(value):
    return Literal(value)
