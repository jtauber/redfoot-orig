from redfoot.rdf.store import storeio

from os.path import dirname, join
import sys
s = dirname(sys.modules[__name__].__file__)

store1 = storeio.TripleStoreIO()

store2 = storeio.TripleStoreIO()
f = open(join(s,"001.rdf"))
store2.input(f, "001.rdf")
f.close()

def print_visitor(s, p, o):
    if o.is_literal():
        x = "L"
    else:
        x = "R"
    print "s='%s', p='%s', o='%s'%s" % (s, p, o, x)

store2.visit(print_visitor, (None, None, None))
import sys
store2.URI = ''
store2.output(sys.stderr)


