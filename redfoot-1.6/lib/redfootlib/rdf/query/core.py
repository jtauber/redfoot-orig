from __future__ import generators


class Query(object):

    def exists(self, subject, predicate, object):
        for triple in self.triples(subject, predicate, object):
            return 1
        return 0

    def first_object(self, subject, predicate):
        for object in self.objects(subject, predicate):
            return object
        return None
 
    def objects_transitive(self, subject, property):
        for object in self.objects(subject, property):
            yield object
            for o in self.objects_transitive(object, property):
                yield o

    def transitive_objects(self, subject, property):
        yield subject
        for object in self.objects(subject, property):
            for o in self.transitive_objects(object, property):
                yield o

    def transitive_subjects(self, predicate, object):
        yield object
        for subject in self.subjects(predicate, object):
            for s in self.transitive_subjects(predicate, object):
                yield s

    
