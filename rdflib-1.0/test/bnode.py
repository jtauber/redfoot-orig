import unittest

from rdflib.triple_store import TripleStore
from rdflib import exception
from rdflib.nodes import URIRef, BNode, Literal

class TypeCheckCase(unittest.TestCase):

    def testA(self):
        store = TripleStore()
        store.load("bnode.rdf", None, 1)
        store.remove_triples(None, None, None)        
        b1 = BNode()
        b2 = BNode()
        self.assertNotEquals(b1, b2)        
        print b1, b2
        store.add(b1, URIRef("foo"), b2)
        store.add(b1, URIRef("foo"), Literal("foo"))
        store.save()

if __name__ == "__main__":
    unittest.main()   
