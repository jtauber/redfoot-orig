import pyexpat

from redfoot.parser import *
from redfoot.store import *
from redfoot.query import *

store = TripleStore()

rdfParser = RDFParser()
rdfParser.setAdder(store.add)

rdfParser.parse("rdfSyntax.rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns")
rdfParser.parse("rdfSchema.rdf", "http://www.w3.org/2000/01/rdf-schema")

qstore = QueryStore()
qstore.setStore(store)

print qstore.get(qstore.CLASS, qstore.TYPE, None)

print qstore.label(qstore.CLASS)
print qstore.comment(qstore.CLASS)

