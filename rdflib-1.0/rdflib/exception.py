class Error(Exception):
    """Base class for rdflib exceptions."""
    pass


class NotOverriddenError(Error):
    """Exception raised for methods unimplemented in derived classes."""

    def __init__(self, meth):
        self.msg = "%s was not overridden in derived class" % meth

    
class NotYetImplemented(Error):
    """RDF li child not allowed."""

    def __init__(self):
        self.msg = "Not yet implemented"


class TypeCheckError(Error):
    """Parts of assertions are subject to type checks."""

    def __init__(self, node):
        self.type = type(node)
        self.node = node


class SubjectTypeError(TypeCheckError):
    """Subject of an assertion must be an instance of URIRef."""

    def __init__(self, node):
        TypeCheckError.__init__(self, node)
        self.msg = "Subject must be instance of URIRef or BNode: %s(%s)" \
                       % (self.node, self.type)


class PredicateTypeError(TypeCheckError):
    """Predicate of an assertion must be an instance of URIRef."""
    def __init__(self, node):
        TypeCheckError.__init__(self, node)
        self.msg = "Predicate must be a URIRef instance: %s(%s)" \
                       % (self.node, self.type)


class ObjectTypeError(TypeCheckError):
    """Object of an assertion must be an instance of URIRef, Literal,
    or BNode."""
    def __init__(self, node):
        TypeCheckError.__init__(self, node)
        self.msg = "Object must be instance of URIRef, Literal, or BNode: %s(%s)" % \
                       (self.node, self.type)


class ParserError(Error):
    """RDF Parser error."""
    pass


class MalformedDescriptionError(ParserError):
    """Descriptions must have either an about or an ID."""

    def __init__(self, name):
        self.name = name
        self.msg = "Descriptions must have either an about or an ID '%s'" % self.name


class ResourceAndCharContentError(ParserError):
    """Node has both character content and a resource attribute."""

    def __init__(self, name):
        self.name = name
        self.msg = "%s has character content and resource attribute" % self.name


class RdfSeqChildNotAllowedError(ParserError):
    """RDF li child not allowed."""

    def __init__(self):
        self.msg = "RDF li child not allowed"


class UnexpectedTypeError(Error):
    """Serializer got object of unexpected type."""

    def __init__(self, object):
        self.object = object
        self.type = type(object)
        self.msg = "Serializer got object of unexpected type: %s(%s)" \
                   % (self.object, self.type)

