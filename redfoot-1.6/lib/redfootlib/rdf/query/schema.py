from __future__ import generators

from redfootlib.rdf.query.core import Query

from redfootlib.rdf.const import LABEL, COMMENT
from redfootlib.rdf.const import TYPE, STATEMENT
from redfootlib.rdf.const import SUBJECT, PREDICATE, OBJECT
from redfootlib.rdf.const import DOMAIN, SUBCLASSOF


class SchemaQuery(Query):

    def label(self, subject, default=None):
        for s, p, o in self.triples(subject, LABEL, None):
            return o
        return default or subject

    def comment(self, subject, default=None):
        for s, p, o in self.triples(subject, COMMENT, None):
            return o
        return default or self.label(subject)
        
    def typeless_resources(self):
        for subject in self.subjects():
            if not self.exists(subject, TYPE, None):
                yield subject

    # TODO: should we have a version of this that answers for subclasses too?
    def is_of_type(self, subject, type):
        return self.exists(subject, TYPE, type)

    def subjects_by_type(self, callback, type, predicate, object):
        for subject in self.subjects(predicate, object):
            if self.is_of_type(subject, type):
                yield subject

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

    def possible_properties(self, type):
        for object in self.transitive_objects(type, SUBCLASSOF):
            for subject in self.subjects(DOMAIN, object):
                yield subject
        
    def possible_properties_for_subject(self, subject):
        for type in self.objects(subject, TYPE):
            for property in self.possible_properties(type):
                yield property

