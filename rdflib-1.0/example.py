from rdflib.triple_store import TripleStore
from rdflib.nodes import URIRef, Literal
from rdflib.const import LABEL

store = TripleStore()
store.load("example.rdf", "http://redfoot.net/2002/06/05/", 1)
store.add(URIRef("http://redfoot.net/"), LABEL, Literal("Redfoot Network Website"))

for s, p, o in store: 
    print s, p, o

for predicate in store.predicates(URIRef("http://redfoot.net/"), None):
    print predicate

store.save()
