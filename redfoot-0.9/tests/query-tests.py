import pyexpat

from redfoot.storeio import *
from redfoot.query import *

store = TripleStore()

storeIO = StoreIO()
storeIO.setStore(store)

storeIO.load("rdfSyntax.rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns")
storeIO.load("rdfSchema.rdf", "http://www.w3.org/2000/01/rdf-schema")

qstore = QueryStore()
qstore.setStore(store)

print qstore.get(qstore.CLASS, qstore.TYPE, None)

print qstore.label(qstore.CLASS)
print qstore.comment(qstore.CLASS)

