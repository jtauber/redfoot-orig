from rdflib.store.memory import InMemoryStore
from rdflib.store.concurrent import Concurrent

from rdflib.store.type_check import TypeCheck

from rdflib.model.schema import Schema

from rdflib.syntax.loadsave import LoadSave


class TripleStore(LoadSave, Schema, TypeCheck, Concurrent, InMemoryStore):
    pass
