
from redfootlib.rdf.query.functors import *
from redfootlib.rdf.query.builders import *

class Query:
    
    def exists(self, subject, predicate, object):
        b = ItemBuilder()
        self.visit(first(triple2statement(b.accept)), (subject, predicate, object))
        return (b.item != None)

    def not_exists(self, subject, predicate, object):
        return not self.exists(subject, predicate, object)

    def get_first(self, subject, predicate, object):
        b = ItemBuilder()
        self.visit(first(triple2statement(b.accept)), (subject, predicate, object))
        return b.item

    def get_first_value(self, subject, predicate, default=None):
        s = self.get_first(subject, predicate, None)
        if s:
            return s.object
        else:
            return default

    # TODO: currently goes into infinite loop if property loops back
    def visit_transitive(self, callback, root, property):
        self.visit(both(callback, o(callback_subject(self.visit_transitive, callback, property))),
                   (root, property, None))

    # TODO: currently goes into infinite loop if property loops back
    def visit_transitive_reverse(self, callback, root, property):
        self.visit(both(callback, s(callback_subject(self.visit_transitive_reverse, callback, property))),
                   (None, property, root))


    # TODO: not really a query
    def generate_uri(self):
        from redfootlib.rdf.store.urigen import generate_uri
        from redfootlib.rdf.objects import resource
        return resource(self.uri + generate_uri())

