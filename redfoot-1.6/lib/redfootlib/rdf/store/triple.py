from redfootlib.rdf.store.urigen import generate_uri as gen_uri
from redfootlib.rdf.objects import resource


class Triple(object):

    def generate_uri(self):
        """Return a new unique uri."""
        return resource(self.uri + gen_uri())

    def remove(self, subject=None, predicate=None, object=None):
        for s, p, o in self.triples(subject, predicate, object):
            super(Triple, self).remove(s, p, o)

    def __iter__(self):
        return self.triples(ANY, ANY, ANY)

    
from redfootlib.rdf.store.memory import InMemoryStore

class TripleStore(Triple, InMemoryStore):
    pass
