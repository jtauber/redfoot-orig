import unittest

from rdflib.syntax.parser import Parser
from rdflib.triple_store import TripleStore
from rdflib.nodes import URIRef, Literal, BNode

from rdflib.exception import ParserError

from rdflib.const import TYPE

TEST = URIRef("http://www.w3.org/2000/10/rdf-tests/rdfcore/testSchema/")

import os
def resolve(rel):
    #return "test_files" + os.sep + rel
    return "http://www.w3.org/2000/10/rdf-tests/rdfcore/" + rel

manifest = TripleStore()
manifest.load("http://www.w3.org/2000/10/rdf-tests/rdfcore/Manifest.rdf")
#manifest.load("Manifest.rdf")        

class ParserTestCase(unittest.TestCase):
        
    def testNegative(self):
        num_failed = 0
        negs = list(manifest.subjects(TYPE, TEST + "NegativeParserTest"))
        negs.sort()
        for neg in negs:
            status = manifest.first_object(neg, TEST + "status")
            if not status=="APPROVED":
                continue
            inDoc = manifest.first_object(neg, TEST + "inputDocument")
            store = TripleStore()
            try:
                store.load(inDoc)
            except ParserError, pe:
                pass
            else:
                print "Failed: '%s'" % inDoc                
                num_failed += 1
        self.assertEquals(num_failed, 0)

    def testPositive(self):
        num_failed = total = 0
        negs = list(manifest.subjects(TYPE, TEST + "PositiveParserTest"))
        negs.sort()
        for neg in negs:
            status = manifest.first_object(neg, TEST + "status")
            if not status=="APPROVED":
                continue
            inDoc = manifest.first_object(neg, TEST + "inputDocument")
            outDoc = manifest.first_object(neg, TEST + "outputDocument")
            out_store = TripleStore()
            out_store.load(outDoc)
            store = TripleStore()
            try:
                store.load(inDoc)
                total += 1
            except ParserError, pe:
                print """
# '%s' failed with %s
""" % (inDoc, pe)
                num_failed += 1
            else:
                if not store == out_store:
                    print """
###
# '%s' failed:
""" % inDoc
                    print """  In:\n"""
                    for s, p, o in store:
                        print "%s %s %s." % (s.n3(), p.n3(), o.n3())
                    print """  Out:\n"""
                    for s, p, o in out_store:
                        print "%s %s %s." % (s.n3(), p.n3(), o.n3())

                    num_failed += 1
                    print """
#
###"""
                    
        self.assertEquals(num_failed, 0, "%s / %s" % (num_failed, total))
            
if __name__ == "__main__":
    unittest.main()   
