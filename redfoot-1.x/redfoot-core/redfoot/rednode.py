
from redfoot.rdf.store.triple import TripleStore
from redfoot.rdf.store.neighbourhood import Neighbourhood
from redfoot.rdf.store.multi import MultiStore
from redfoot.rdf.store.storeio import LoadSave
from redfoot.rdf.store.autosave import AutoSave
from redfoot.neighbour_manager import NeighbourManager
from redfoot.rdf.query.schema import SchemaQuery
from redfoot import rdf_files


class RedNode(SchemaQuery, NeighbourManager, AutoSave, LoadSave, TripleStore):
    """
    A RedNode is a store that is queryable via high level queries, can
    manage its neighbour connections, [automatically] save to RDF, and
    load from RDF.

    A RedNode contains a neighbourhood store for querying the nodes'
    entire neighbourhood, which includes itself and its neighbours in
    that order.
    """

    def __init__(self):
        super(RedNode, self).__init__()
        neighbours = Neighbours()
        neighbours.add_store(rdf_files.schema)
        neighbours.add_store(rdf_files.syntax)
        neighbours.add_store(rdf_files.builtin)
        self.neighbourhood = RedNeighbourhood(self, neighbours)
        self.neighbours = neighbours        


class Neighbours(SchemaQuery, MultiStore):
    """
    A store of the multiple stores, the neighbours, that is queryable
    via high level queries.

    MultiStore is a store that makes multiple stores look like a
    single store.
    """


class RedNeighbourhood(SchemaQuery, Neighbourhood):
    """
    A store of the neighbourhood that is queryable via high level
    queries.
    
    A Neighbourhood is a store that contains a local store and a store
    of neighbours in which the local store gets visited first and then
    the neighbours in order that they where added.
    """


