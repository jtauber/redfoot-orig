from rdflib.const import LABEL, TYPE
from rdflib.nodes import URIRef, Literal

NEIGHBOUR = URIRef("http://redfoot.sourceforge.net/2001/04/neighbour#Neighbour")
CONNECTED = URIRef("http://redfoot.sourceforge.net/2001/04/neighbour#Connected")
YES = URIRef("http://redfoot.sourceforge.net/2000/10/06/builtin#YES")
NO = URIRef("http://redfoot.sourceforge.net/2000/10/06/builtin#NO")

from rdflib.triple_store import TripleStore

class Neighbour(TripleStore): pass

class NeighbourManager(object):

    def load(self, location, uri, create=0):
        super(NeighbourManager, self).load(location, uri, create)
        # load neighbours that are marked as connected
        for subject in self.subjects_by_type(NEIGHBOUR, CONNECTED, YES):
            self._connect(subject)

    def _connect(self, neighbour):
        self.connect_to(neighbour)

    def connect_to(self, location, uri=None):
        neighbour = Neighbour()        
        neighbour.load(location, uri or location, 0)
        self.neighbours.append_store(neighbour)
        self.remove(URIRef(location), TYPE, NEIGHBOUR)
        self.add(URIRef(location), TYPE, NEIGHBOUR)        
        self.remove_triples(URIRef(location), CONNECTED, None)
        self.add(URIRef(location), CONNECTED, YES)        

    def disconnect_from(self, uri):
        for store in [store for store in self.neighbours if store.uri==uri]:
            self.neighbours.remove(store)
            self.remove_triples(URIRef(uri), CONNECTED, None)
            self.add(URIRef(uri), CONNECTED, NO)
            # Do we want to remember our neighbour?
            if not self.exists(URIRef(uri), TYPE, NEIGHBOUR):
                self.add(URIRef(uri), TYPE, NEIGHBOUR)
