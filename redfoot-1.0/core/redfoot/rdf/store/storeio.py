from string import find

class StoreIO:
    """Store I/O.

    Mixed-in with a store that implements add and visit and provides I/O
    for that class using rdf.syntax.parser and rdf.syntax.serializer
    """
    
    def __init__(self):
        self.URI = None

    def load(self, location, URI=None):
        self.location = location
        if URI==None:
            # default to location
            self.URI = self.location
        else:
            self.URI = URI

        if find(location, '://')<0: # is relative
            from urllib import url2pathname
            path = url2pathname(location) 
            import os
            # TODO: is this equiv to os.path.exists?            
            if not os.access(path, os.F_OK): 
                self.save(path, None)
            
        self.parse_URI(self.location, self.URI)

    def save(self, location=None, URI=None):
        if location==None:
            location = self.location
        if URI==None:
            URI = self.URI
        stream = open(location, 'w')
        self.output(stream, URI)
        stream.close()
        
from redfoot.rdf.store.triple import TripleStore
from redfoot.rdf.syntax.parser import Parser
from redfoot.rdf.syntax.serializer import RedSerializer

class TripleStoreIO(StoreIO, Parser, RedSerializer, TripleStore):
    """Mix-in of StoreIO and TripleStore."""
    
    def __init__(self):
        TripleStore.__init__(self)
        RedSerializer.__init__(self)

