from redfootlib.rdf.store.memory import InMemoryStore
from redfootlib.rdf.store.concurrent import Concurrent


class TripleStore(Concurrent, InMemoryStore):
    pass
