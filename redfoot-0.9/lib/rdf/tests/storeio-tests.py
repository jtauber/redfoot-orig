from redfoot.store import TripleStore
from redfoot.storeio import StoreIO

def test_1():
    ""

    tripleStore = TripleStore()

    storeIO = StoreIO()
    storeIO.setStore(tripleStore)
    storeIO.load("http://www.w3.org/1999/02/22-rdf-syntax-ns")

    storeIO.saveAs("tmptmp.test", "tmptmp.test")
    
def test_2():
    ""

    pass
    

test_1()
test_2()
