from __future__ import generators

from redfootlib.rdf.nodes import URIRef

from time import time, gmtime

def generate_path():
    sn = 0
    last_time_path = None
    while 1:
        t = time()
        year, month, day, hh, mm, ss, wd, y, z = gmtime(t)           
        time_path = "%0004d/%02d/%02d/T%02d/%02d/%02dZ" % ( year, month, day, hh, mm, ss)

        if time_path==last_time_path:
            sn = sn + 1
        else:
            sn = 0
            last_time_path = time_path

        path = time_path + "%.004d" % sn
        yield path

path_generator = generate_path()

class Core(object):


    def generate_uri(self):
        """Return a new unique uri."""
        return URIRef(self.uri + path_generator.next())
    
    def remove(self, subject=None, predicate=None, object=None):
        for s, p, o in self.triples(subject, predicate, object):
            super(Core, self).remove(s, p, o)

    def exists(self, subject, predicate, object):
        for triple in self.triples(subject, predicate, object):
            return 1
        return 0

    def first_object(self, subject, predicate):
        for object in self.objects(subject, predicate):
            return object
        return None
 
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

    
