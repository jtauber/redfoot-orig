from __future__ import generators

class MultiStore(object):
    """
    An ordered collection of stores with a 'visit' facade that visits all
    stores.
    """
    
    def __init__(self):
        super(MultiStore, self).__init__()
        self.stores = []

    def add_store(self, store):
        stores = self.stores
        if not store in stores:
            stores.append(store)

    def remove_store(self, store):
        stores = self.stores
        if store and store in stores:
            stores.remove(store)

    def triples(self, s, p, o):
        for store in self.stores:
            for triple in store.triples(s, p, o):
                yield triple

    def subjects(self, p, o):
        for store in self.stores:
            for subject in store.subjects(p, o):
                yield subject

    def objects(self, s, p):
        for store in self.stores:
            for object in store.objects(s, p):
                yield object

    def visit(self, callback, triple):
        for store in self.stores:
            stop = store.visit(callback, triple)
            if stop:
                return stop

