from redfootlib.rdf.store.memory import InMemoryStore
from redfootlib.rdf.store.concurrent import Concurrent

from redfootlib.rdf.store.type_check import TypeCheck

from redfootlib.rdf.model.schema import Schema

from redfootlib.rdf.syntax.loadsave import LoadSave


class TripleStore(LoadSave, Schema, TypeCheck, Concurrent, InMemoryStore):
    pass
