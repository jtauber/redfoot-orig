from string import find

class StoreIO:
    """Store I/O.

    Mixed-in with a store that implements add and visit and provides I/O
    for that class using rdf.syntax.parser and rdf.syntax.serializer
    """
    
    def __init__(self):
        self.uri = None

    def load(self, location, uri=None, create=0):
        self.location = location
        if uri==None:
            # default to location
            self.uri = self.location
        else:
            self.uri = uri

        if create and find(location, '://')<0: # is relative
            from urllib import url2pathname
            path = url2pathname(location) 
            import os
            # TODO: is this equiv to os.path.exists?            
            if not os.access(path, os.F_OK): 
                self.save(path, None)
            
        self.parse_URI(self.location, self.uri)

    def save(self, location=None, uri=None):
        if location==None:
            location = self.location
        if uri==None:
            uri = self.uri
        stream = open(location, 'w')
        self.output(stream, uri)
        stream.close()
        
from redfoot.rdf.store.triple import TripleStore
from redfoot.rdf.syntax.parser import Parser
from redfoot.rdf.syntax.serializer import RedSerializer

class TripleStoreIO(StoreIO, Parser, RedSerializer, TripleStore):
    """Mix-in of StoreIO and TripleStore."""
    
    def __init__(self):
        TripleStore.__init__(self)
        RedSerializer.__init__(self)

