# TODO: seems like rednode should live under redfoot.rdf... move there?

from redfoot.rdf.query.schema import SchemaQuery

from redfoot.rdf.store.storeio import StoreIO, TripleStoreIO
from redfoot.rdf.store.autosave import AutoSaveStoreIO

from redfoot.rdf.query.functors import *
from redfoot.rdf.const import *

class Local(SchemaQuery, TripleStoreIO):
    """A read/write store of RDF statements - a mixin of Query and TripleStoreIO."""
    pass


#class JournalingStoreLocal(SchemaQuery, JournalingStoreIO):
#    """Like Local but for journaling stores."""
#    pass


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
        # TODO: There may be an issue of order here. If so, we
        # probably need to either reimplement this to explicitly call
        # local first (and depending on what it returns call
        # neighbours. Or, maybe we need to do this at the level of the
        # neighbourhood's visit... in which case we may need to
        # subclass Multistore or give it a notion of order.
        return self.neighbourhood.visit(callback, triple)

    ### Overridden from SchemaQuery

    # TODO both this and the visit_subclasses in SchemaQuery can probably be cleaned up so there is more reuse
    # between the two
    def visit_subclasses(self, class_start_callback, class_end_callback, instance_callback, root,
                         recurse=1, depth=0):
        class_start_callback(root, depth)

        def f(type,
              self=self, class_start_callback=class_start_callback,
              class_end_callback=class_end_callback, instance_callback=instance_callback, depth=depth):
            self.visit_subclasses(class_start_callback, class_end_callback, instance_callback,
                                  type, 1, depth + 1)

        def g(instance,
              depth=depth, instance_callback=instance_callback):
            instance_callback(instance, depth)

        def h(klass,
              depth=depth, class_start_callback=class_start_callback, class_end_callback=class_end_callback):
            class_start_callback(klass, depth + 1)
            class_end_callback(klass, depth + 1)

        if recurse:
            self.neighbourhood.visit(s(f), (None, SUBCLASSOF, root))
        else:
            self.neighbourhood.visit(s(h), (None, SUBCLASSOF, root))

        self.local.visit(s(g), (None, TYPE, root))

        class_end_callback(root, depth)

    def visit_typeless_resources(self, callback):
        self.local.visit_subjects(filter(s(callback), not_subject(self.exists, TYPE, None)))

