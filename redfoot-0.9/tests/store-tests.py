import pyexpat

from redfoot.parser import *
from redfoot.store import *

class RDFParser:

    def __init__(self, baseURI, URL, adder):
        parser = pyexpat.ParserCreate(namespace_separator="")
        if baseURI!=None:
            parser.SetBase(baseURI)
            rootHandler(parser, adder, None)
            from urllib import *
            f = urlopen(URL)
            parser.ParseFile(f)
            f.close()

def test_1():
    "load RDF from url"

    url = "http://www.w3.org/1999/02/22-rdf-syntax-ns"
    url = "rdfSchema.rdf"
    uri = url

    store = RDFStore()

    parser = RDFParser(uri, url, store.add)
#    parser = RDFParser()
#    parser.setAdder(store.add)
#    parser.setURL(url)
#    parser.setURI(uri)

#    parser.parse()
    
    print len(store.get())

test_1()
