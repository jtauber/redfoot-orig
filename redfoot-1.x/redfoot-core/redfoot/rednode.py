from redfoot.rdf.store.triple import TripleStore
from redfoot.rdf.query.schema import SchemaQuery

from redfoot.rdf.store.multi import MultiStore
from redfoot.rdf.store.storeio import LoadSave
from redfoot.rdf.store.autosave import AutoSave

from redfoot import rdf_files

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

from redfoot.neighbour_manager import NeighbourManager, NEIGHBOUR, CONNECTED, YES, NO


import redfoot
from redfoot.command_line import process_args
from redfoot.server import RedServer

    
class RedNode(SchemaQuery, NeighbourManager, AutoSave, LoadSave, TripleStore):

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

