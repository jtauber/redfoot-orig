import pyexpat

from redfoot.store import *
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

store.add("vehicle", qstore.TYPE, qstore.CLASS)
store.add("vehicle", qstore.SUBCLASSOF, qstore.RESOURCE)
store.add("car", qstore.TYPE, qstore.CLASS)
store.add("car", qstore.SUBCLASSOF, "vehicle")
store.add("my-car", qstore.TYPE, "car")
store.add("my-car", qstore.LABEL, "^My Car")

print qstore.getByType("car", None, None)
print qstore.getByType("car", qstore.LABEL, "^My Car")

print qstore.isOfType("my-car", "car")
print qstore.isOfType("my-car", "vehicle")
print qstore.isOfType("my-car", "giraffe")

store.add("car", qstore.SUBCLASSOF, "fast-things")

print qstore.typeInh("car")

print qstore.transitiveSuperTypes("car")

print qstore.transitiveSubTypes("vehicle")
