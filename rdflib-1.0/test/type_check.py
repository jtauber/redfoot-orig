import unittest

from rdflib.triple_store import TripleStore
from rdflib import exception
from rdflib.nodes import URIRef

foo = URIRef("foo")


class TypeCheckCase(unittest.TestCase):
    def setUp(self):
        self.store = TripleStore()
        
    def testSubjectTypeCheck(self):
        self.assertRaises(exception.SubjectTypeError,
                          self.store.add, None, foo, foo)

    def testPredicateTypeCheck(self):
        self.assertRaises(exception.PredicateTypeError,
                          self.store.add, foo, None, foo)

    def testObjectTypeCheck(self):
        self.assertRaises(exception.ObjectTypeError,
                          self.store.add, foo, foo, None)
