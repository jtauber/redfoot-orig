import unittest

from rdflib.syntax.parser import Parser
from rdflib.triple_store import TripleStore
from rdflib.nodes import URIRef, Literal

from rdflib import exception

import os
def resolve(rel):
    return "test_files" + os.sep + rel

class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.store = TripleStore()

    def test_amp_in_url_001(self):
        self.store.load(resolve("amp-in-url/test001.rdf"))
        s1 = URIRef("http://example/q?abc=1&def=2")
        self.assertEqual(self.store.exists(s1, None, None), 1)

    def test_unrecognised_xml_attributes_001(self):
        self.store.load(resolve("unrecognised-xml-attributes/test001.rdf"))
        self.assertEqual(self.store.exists(None, None, Literal("default")), 0)
        self.assertEqual(self.store.exists(None, None, Literal("anything")), 0)

    def test_unrecognised_xml_attributes_002(self):
        self.store.load(resolve("unrecognised-xml-attributes/test002.rdf"))
        self.assertEqual(self.store.exists(None, None, Literal("anything")), 0)

    def test_rdf_charmod_literals_test001(self):
        self.store.load(resolve("rdf-charmod-literals/test001.rdf"))
        self.assertEqual(self.store.exists(None, None, Literal("Dürst")), 1)

    def test_rdf_charmod_literals_error002(self):
        self.store.load(resolve("rdf-charmod-literals/error002.rdf"))
        self.assertEqual(1, 0)


    def test_rdf_containers_syntax_vs_schema_test001(self):
        self.store.load(resolve("rdf-containers-syntax-vs-schema/test001.rdf"))
        ONE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#_1")
        TWO = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#_2")
        BAG = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag")
        TYPE = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
        s = None # Match any for now
        self.assertEqual(self.store.exists(s, ONE, Literal("1")), 1)
        self.assertEqual(self.store.exists(s, TWO, Literal("2")), 1)
        self.assertEqual(self.store.exists(s, TYPE, BAG), 1)

    def test_rdf_containers_syntax_vs_schema_test002(self):
        self.store.load(resolve("rdf-containers-syntax-vs-schema/test002.rdf"))
        for s, p, o in self.store:
            print s.n3(), p.n3(), o.n3()
        _ = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#_")
        s = None # Match any for now
        self.assertEqual(len(list(self.store)), 5)
        self.assertEqual(self.store.exists(s, _ + "1", Literal("_1")), 1)
        self.assertEqual(self.store.exists(s, _ + "1", Literal("1")), 1)
        self.assertEqual(self.store.exists(s, _ + "3", Literal("_3")), 1)
        #self.assertEqual(self.store.exists(s, _ + "2", Literal("2")), 1)
        #self.assertEqual(self.store.exists(s, TYPE, BAG), 1)

        
    def test_rdf_containers_syntax_vs_schema_test003(self):
        self.store.load(resolve("rdf-containers-syntax-vs-schema/test003.rdf"))
        self.assertEqual(1, 0)
        
    def test_rdf_containers_syntax_vs_schema_test004(self):
        self.store.load(resolve("rdf-containers-syntax-vs-schema/test004.rdf"))
        self.assertEqual(1, 0)
        
    def test_rdf_containers_syntax_vs_schema_test006(self):
        self.store.load(resolve("rdf-containers-syntax-vs-schema/test006.rdf"))
        self.assertEqual(1, 0)            
            
    def test_rdf_containers_syntax_vs_schema_test007(self):
        self.store.load(resolve("rdf-containers-syntax-vs-schema/test007.rdf"))
        self.assertEqual(1, 0)            
            
    def test_rdf_containers_syntax_vs_schema_test008(self):
        self.store.load(resolve("rdf-containers-syntax-vs-schema/test008.rdf"))
        self.assertEqual(1, 0)            
            
if __name__ == "__main__":
    unittest.main()   
