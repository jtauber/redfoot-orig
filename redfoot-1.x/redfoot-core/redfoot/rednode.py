import redfoot, sys

from redfoot.rdf.query.schema import SchemaQuery

from redfoot.rdf.store.storeio import StoreIO, TripleStoreIO
from redfoot.rdf.store.autosave import AutoSaveStoreIO

from redfoot.rdf.const import LABEL, TYPE
from redfoot.rdf.objects import resource, literal

from redfoot.command_line import process_args
from redfoot.server import RedServer

NEIGHBOUR = resource("http://redfoot.sourceforge.net/2001/04/neighbour#Neighbour")
CONNECTED = resource("http://redfoot.sourceforge.net/2001/04/neighbour#Connected")
YES = resource("http://redfoot.sourceforge.net/2000/10/06/builtin#YES")
NO = resource("http://redfoot.sourceforge.net/2000/10/06/builtin#NO")


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

    def __init__(self, uri=None, autosave=1):
        self.uri = uri
        if autosave:
            self.local = AutoSaveLocal() # local only
        else:
            self.local = Local() # local only
        self.neighbours = MultiStore() # neighbours only

        self.neighbourhood = MultiStore() # neighbourhood = local + neighbours

        # local should be the first store as they are visited in order
        self.neighbourhood.add_store(self.local) 
        self.neighbourhood.add_store(self.neighbours)

        self.neighbours.add_store(schema)
        self.neighbours.add_store(syntax)
        self.neighbours.add_store(builtin)


    #def run(self, address=None, port=8080, blocking=1):
    def run(self, **args):
        "This method blocks until the server is shutdown"
        if len(args)==0:
            (uri, rdf, address, port) =  process_args()
            apps = redfoot.get_apps()
            Boot = None
        else:
            # TODO: get defaults from common source instead of keeping
            # them in sync with process_args defaults
            uri = args.get('uri', 'TODO: compute')
            rdf = args.get('rdf', 'rednode.rdf')
            self.load(rdf, uri, 1)
            address = args.get('address', '')
            port = args.get('port', 8080)
            Boot = args.get('Boot', None)

        if not Boot:
            if len(apps)==0:
                raise "No Apps Found"
            else:
                # TODO: add way to specify Boot
                uri, app_class = apps[0]
                Boot = app_class
            self.load(rdf, uri, 1)

        self.server = server = RedServer(address, port)
        server.add_app(Boot(self))        
        server.run()
            
    def load(self, location, uri, create=0):
        self.uri = uri
        self.local.load(location, uri, create)
        # load neighbours that are marked as connected
        self.local.visit_by_type(self._connect, NEIGHBOUR, CONNECTED, YES)

    def _connect(self, neighbour, p, o):
        self.connect_to(neighbour.uri)

    def connect_to(self, location, uri=None):
        uri = uri or location

        storeIO = TripleStoreIO()        
        storeIO.load(location, uri, 0)
        self.neighbours.add_store(storeIO)
        self.remove(resource(location), TYPE, NEIGHBOUR)
        self.add(resource(location), TYPE, NEIGHBOUR)        
        self.remove(resource(location), CONNECTED, None)
        self.add(resource(location), CONNECTED, YES)        

    def disconnect_from(self, uri):
        for store in [store for store in self.neighbours.stores if store.uri==uri]:
            self.neighbours.remove_store(store)
            self.remove(resource(uri), CONNECTED, None)
            self.add(resource(uri), CONNECTED, NO)
            # Do we want to remember our neighbour?
            if not self.local.exists(resource(uri), TYPE, NEIGHBOUR):
                self.add(resource(uri), TYPE, NEIGHBOUR)
    ###

    def add(self, s, p, o):
        self.local.add(s, p, o)
        
    def remove(self, subject, predicate, object):
        self.local.remove(subject, predicate, object)

    def visit(self, callback, triple):
        return self.neighbourhood.visit(callback, triple)

