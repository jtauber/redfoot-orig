import redfoot

from redfoot import rdf_files

from redfoot.rdf.query.schema import SchemaQuery

from redfoot.rdf.const import LABEL, TYPE
from redfoot.rdf.objects import resource, literal

from redfoot.command_line import process_args
from redfoot.server import RedServer

NEIGHBOUR = resource("http://redfoot.sourceforge.net/2001/04/neighbour#Neighbour")
CONNECTED = resource("http://redfoot.sourceforge.net/2001/04/neighbour#Connected")
YES = resource("http://redfoot.sourceforge.net/2000/10/06/builtin#YES")
NO = resource("http://redfoot.sourceforge.net/2000/10/06/builtin#NO")

from redfoot.rdf.store.multi import MultiStore
from redfoot.rdf.store.storeio import LoadSave
from redfoot.rdf.store.autosave import AutoSave


class Local(SchemaQuery, LoadSave, TripleStore): pass
class Neighbour(LoadSave, TripleStore): pass
class Neighbours(SchemaQuery, MultiStore): pass


class Neighbourhood(SchemaQuery, object):
    def __init__(self, local, neighbours):
        super(Neighbourhood, self).__init__()
        self.local = local
        self.neighbours = neighbours

    def visit(self, callback, triple):
        stop = self.local.visit(callback, triple)
        if stop:
            return stop
        stop = self.neighbours.visit(callback, triple)
        if stop:
            return stop

    
class RedNode(SchemaQuery, AutoSave, LoadSave, TripleStore):

    def __init__(self):
        super(RedNode, self).__init__()
        self.local = self # TODO: temp
        neighbours = Neighbours()
        neighbours.add_store(rdf_files.schema)
        neighbours.add_store(rdf_files.syntax)
        neighbours.add_store(rdf_files.builtin)
        self.neighbourhood = Neighbourhood(self, neighbours)
        self.neighbours = neighbours        

    def run(self, **args):
        "This method blocks until the server is shutdown"
        if len(args)==0:
            (rdf_uri, rdf, address, port) =  process_args()
            apps = redfoot.get_apps()
            Boot = None
        else:
            # TODO: get defaults from common source instead of keeping
            # them in sync with process_args defaults
            rdf_uri = args.get('uri', 'TODO: compute')
            rdf = args.get('rdf', 'rednode.rdf')
            self.load(rdf, rdf_uri, 1)
            address = args.get('address', '')
            port = args.get('port', 8080)
            Boot = args.get('Boot', None)

        if not Boot:
            if len(apps)==0:
                raise "No Apps Found"
            else:
                # TODO: add way to specify Boot
                app_uri, app_class = apps[0]
                Boot = app_class
            self.load(rdf, rdf_uri, 1)

        self.server = server = RedServer(address, port)
        server.add_app(Boot(self))        
        server.run()

    def load(self, location ,uri, create=0):
        super(RedNode, self).load(location, uri, create)
        # load neighbours that are marked as connected
        self.local.visit_by_type(self._connect, NEIGHBOUR, CONNECTED, YES)

    def _connect(self, neighbour, p, o):
        self.connect_to(neighbour.uri)

    def connect_to(self, location, uri=None):
        neighbour = Neighbour()        
        neighbour.load(location, uri or location, 0)
        self.neighbours.add_store(neighbour)
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


