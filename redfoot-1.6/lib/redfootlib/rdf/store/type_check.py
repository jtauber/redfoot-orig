from redfootlib.rdf.nodes import URIRef, Literal, BNode


class TypeCheck(object):

    def __init__(self):
        super(TypeCheck, self).__init__()
        
    def add(self, subject, predicate, object):
        self.check(subject, predicate, object)
        super(TypeCheck, self).add(subject, predicate, object)

    def remove(self, subject, predicate, object):
        self.check(subject, predicate, object)        
        super(TypeCheck, self).remove(subject, predicate, object)            

    def triples(self, subject, predicate, object):
        if subject:
            self.check_subject(subject)
        if predicate:
            self.check_predicate(predicate)
        if object:
            self.check_object(object)
        return super(TypeCheck, self).triples(subject, predicate, object)
        
    # TODO: should the following check methods be module level instead?
    def check(self, subject, predicate, object):
        self.check_subject(subject)
        self.check_predicate(predicate)
        self.check_object(object)

    def check_subject(self, s):
        if not (isinstance(s, URIRef) or isinstance(s, BNode)):
            raise "subject must either be a URIRef or BNode: %s(%s)" % (s, type(s))
    def check_predicate(self, p):
        if not isinstance(p, URIRef):
            raise "predicate must by a URIRef: %s(%s)" % (p, type(p))

    def check_object(self, o):
        if not (isinstance(o, URIRef) or \
           isinstance(o, Literal) or \
           isinstance(o, BNode)):
            raise "object must be one of URIRef, Literal or BNode: %s(%s)" % (o, type(o))

