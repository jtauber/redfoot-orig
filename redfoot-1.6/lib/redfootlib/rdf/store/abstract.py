from __future__ import generators


class AbstractStore(object):

    def add(self, subject, predicate, object):
        raise "Must override"

    def remove(self, subject, predicate, object):
        raise "Must override"
    
    def triples(self, subject, predicate, object):
        raise "Must override"
    
    def subjects(self, predicate=None, object=None):
        for s, p, o in self.triples(None, predicate, object):
            yield s

    def predicates(self, subject=None, object=None):
        for s, p, o in self.triples(subject, None, object):
            yield p

    def objects(self, subject=None, predicate=None):
        for s, p, o in self.triples(subject, predicate, None):
            yield o

    def __iter__(self):
        return self.triples(None, None, None)
