from redfootlib.rdf.query.core import Query

from redfootlib.rdf.const import LABEL, COMMENT
from redfootlib.rdf.const import TYPE, STATEMENT
from redfootlib.rdf.const import SUBJECT, PREDICATE, OBJECT


class SchemaQuery(Query):

    # TODO: should we have a version of this that answers for subclasses too?
    def is_of_type(self, subject, type):
        return self.exists(subject, TYPE, type)

    def label(self, subject, default=None):
        for s, p, o in self.triples(subject, LABEL, None):
            return o
        return default or subject

    def comment(self, subject, default=None):
        for s, p, o in self.triples(subject, COMMENT, None):
            return o
        return default or self.label(subject)
        
    def get_statement_uri(self, subject, predicate, object):
        """\
        Returns the first statement uri for the given subject, predicate, object.
        """
        for (s, p, o) in self.triples(None, TYPE, STATEMENT):
            if self.exists(s, SUBJECT, subject)\
            and self.exists(s, PREDICATE, predicate)\
            and self.exists(s, OBJECT, object):
                return s
        return None

