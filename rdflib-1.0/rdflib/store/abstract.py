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

    def subject_predicates(self, object=None):
        for s, p, o in self.triples(None, None, object):
            yield s, p
            
    def subject_objects(self, predicate=None):
        for s, p, o in self.triples(None, predicate, None):
            yield s, o
        
    def predicate_objects(self, subject=None):
        for s, p, o in self.triples(subject, None, None):
            yield p, o

    def __iter__(self):
        return self.triples(None, None, None)
