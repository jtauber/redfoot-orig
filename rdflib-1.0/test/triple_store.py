import unittest

from rdflib.store.abstract import AbstractStore
from rdflib import exception

class AbstractStoreTest(unittest.TestCase):
    def setUp(self):
        self.store = AbstractStore()

    def testAdd(self):
        self.assertRaises(exception.NotOverriddenError,
                          self.store.add, None, None, None)

    def testRemove(self):
        self.assertRaises(exception.NotOverriddenError,
                          self.store.remove, None, None, None)

    def testTriples(self):
        self.assertRaises(exception.NotOverriddenError,
                          self.store.triples, None, None, None)


if __name__ == "__main__":
    unittest.main()   


