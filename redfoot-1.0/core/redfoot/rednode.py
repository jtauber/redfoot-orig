# TODO: seems like rednode should live under redfoot.rdf... move there?

from redfoot.rdf.query.schema import SchemaQuery

from redfoot.rdf.store.storeio import StoreIO, TripleStoreIO
from redfoot.rdf.store.autosave import AutoSaveStoreIO

from redfoot.rdf.query.functors import *
from redfoot.rdf.const import *

class Local(SchemaQuery, TripleStoreIO):
    """A read/write store of RDF statements - a mixin of Query and TripleStoreIO."""
    pass


class AutoSaveLocal(SchemaQuery, AutoSaveStoreIO):
    """Like Local but for auto-saving stores."""
    pass


class MultiStore(SchemaQuery, StoreIO):
    """An ordered collection of stores with a 'visit' facade that visits all stores."""
    
    def __init__(self):
        StoreIO.__init__(self)
        self.stores = []

    def add_store(self, store):
        stores = self.stores
        if not store in stores:
            stores.append(store)

    def remove_store(self, store):
        stores = self.stores
        if store and store in stores:
            stores.remove(store)

    def visit(self, callback, triple):
        for store in self.stores:
            stop = store.visit(callback, triple)
            if stop:
                return stop

# TODO this belongs elsewhere (make generic first)
def to_relative_URL(path):
    import sys
    from os.path import join, dirname
    from urllib import pathname2url
    libDir = dirname(sys.modules["redfoot.rednode"].__file__)
    return pathname2url(join(libDir, path))


schema = TripleStoreIO()
schema.load(to_relative_URL("rdf_files/rdfSchema.rdf"), "http://www.w3.org/2000/01/rdf-schema")

syntax = TripleStoreIO()
syntax.load(to_relative_URL("rdf_files/rdfSyntax.rdf"), "http://www.w3.org/1999/02/22-rdf-syntax-ns")

builtin = TripleStoreIO()
builtin.load(to_relative_URL("rdf_files/builtin.rdf"), "http://redfoot.sourceforge.net/2000/10/06/builtin")

class RedNode(SchemaQuery):

    def __init__(self, autosave=1):
        self.URI = "??"
        if autosave:
            self.local = AutoSaveLocal() # local only
        else:
            self.local = Local() # local only
        self.neighbours = MultiStore() # neighbours only

        self.neighbourhood = MultiStore() # neighbourhood = local + neighbours
        # local should be the first store as they are visited in order
        self.neighbourhood.add_store(self.local) 
        self.neighbourhood.add_store(self.neighbours)

        # TODO: we need to reuse the same triple stores for the
        # following instead of loading a new copy of each for ever
        # RedNode
        self.neighbours.add_store(schema)
        self.neighbours.add_store(syntax)
        self.neighbours.add_store(builtin)

    def connect_to(self, location, URI=None):
        URI = URI or location

        storeIO = TripleStoreIO()        
        storeIO.load(location, URI)
        self.neighbours.add_store(storeIO)

    ###

    def add(self, s, p, o):
        self.local.add(s, p, o)
        
    def remove(self, subject, predicate, object):
        self.local.remove(subject, predicate, object)

    def visit(self, callback, triple):
        return self.neighbourhood.visit(callback, triple)

