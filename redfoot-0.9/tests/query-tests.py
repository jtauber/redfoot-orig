import pyexpat

from redfoot.parser import *
from redfoot.store import *
from redfoot.query import *

store = TripleStore()

parser = pyexpat.ParserCreate(namespace_separator="")
parser.SetBase("http://www.w3.org/1999/02/22-rdf-syntax-ns")
rootHandler(parser, store.add, None)
f = open("rdfSyntax.rdf")
parser.ParseFile(f)
f.close()

parser = pyexpat.ParserCreate(namespace_separator="")
parser.SetBase("http://www.w3.org/2000/01/rdf-schema")
rootHandler(parser, store.add, None)
f = open("rdfSchema.rdf")
parser.ParseFile(f)
f.close()

qstore = QueryStore()
qstore.setStore(store)

print qstore.get(qstore.CLASS, qstore.TYPE, None)

print qstore.label(qstore.CLASS)
print qstore.comment(qstore.CLASS)

