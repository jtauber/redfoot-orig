from redfoot.rdf.const import LABEL, TYPE
from redfoot.rdf.objects import resource, literal

NEIGHBOUR = resource("http://redfoot.sourceforge.net/2001/04/neighbour#Neighbour")
CONNECTED = resource("http://redfoot.sourceforge.net/2001/04/neighbour#Connected")
YES = resource("http://redfoot.sourceforge.net/2000/10/06/builtin#YES")
NO = resource("http://redfoot.sourceforge.net/2000/10/06/builtin#NO")

from redfoot.rednode import Neighbour

class NeighbourManager(object):

    def load(self, location ,uri, create=0):
        super(NeighbourManager, self).load(location, uri, create)
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
