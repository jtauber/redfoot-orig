from redfoot.rdf.syntax.serializer import RedSerializer
from redfoot.rdf.store.triple import TripleStore
from redfoot.rdf.objects import resource, literal

class TestStore(RedSerializer, TripleStore):
    """Mix-in of StoreIO and TripleStore."""
    
    def __init__(self):
        TripleStore.__init__(self)
        RedSerializer.__init__(self)        


def run():
    store = TestStore()
    store.add(resource("john"), resource("age"), literal("37"))
    store.add(resource("paul"), resource("age"), literal("35"))
    store.add(resource("paul"), resource("foo"), literal("bar"))    
    store.add(resource("peter"), resource("age"), literal("35"))
    
    import sys
    store.output(sys.stdout)
    
    return (2, '')

