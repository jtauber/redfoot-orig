import pyexpat

from redfoot.parser import *
from redfoot.store import *
from redfoot.query import *

store = TripleStore()

rdfParser = RDFParser()
rdfParser.setBaseURI("http://www.w3.org/1999/02/22-rdf-syntax-ns")
rdfParser.setURL("rdfSyntax.rdf")
rdfParser.setAdder(store.add)
rdfParser.parse()

rdfParser.setBaseURI("http://www.w3.org/2000/01/rdf-schema")
rdfParser.setURL("rdfSchema.rdf")
rdfParser.setAdder(store.add)
rdfParser.parse()

qstore = QueryStore()
qstore.setStore(store)

print qstore.get(qstore.CLASS, qstore.TYPE, None)

print qstore.label(qstore.CLASS)
print qstore.comment(qstore.CLASS)

