
def test_1():
    "load RDF from url"

    from redfoot.store import TripleStore
    store = TripleStore()

    from redfoot.parser import RDFParser
    parser = RDFParser()

    parser.setAdder(store.add)

    parser.parse("http://www.w3.org/1999/02/22-rdf-syntax-ns")
    
    print len(store.get())


def test_2():
    "NeighborhoodStore test"
    pass
    

test_1()
test_2()

