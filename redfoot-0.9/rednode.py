# $Header$

from redfoot.store import TripleStore

class MultiStore:
    ""
    
    def __init__(self):
        self.stores = {}

    def addStore(self, store):
        self.stores[store] = 1

    def getStores(self):
        return self.stores.keys()

    def visit(self, visitor, subject=None, property=None, value=None):
        for store in self.getStores():
            store.visit(visitor, subject, property, value)

    def get(self, subject=None, property=None, value=None):
        class Visitor:
            def __init__(self):
                self.list = []

            def callback(self, subject, property, value):
                self.list.append((subject, property, value))

        self.visit(visitor, subject, property, value)
        
	return visitor.list
        
        
class StoreNode:
    ""

    def __init__(self):
        self.stores = MultiStore()

        from redfoot.storeio import StoreIO

        storeIO = StoreIO()
        storeIO.setStore(TripleStore())
        storeIO.load("tests/rdfSchema.rdf", "http://www.w3.org/2000/01/rdf-schema")
        self.connectTo(storeIO.getStore())
        
        storeIO = StoreIO()
        storeIO.setStore(TripleStore())
        storeIO.load("tests/rdfSyntax.rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns")
        self.connectTo(storeIO.getStore())


    def _preCacheRemoteStores(self, baseDirectory=None):
        rstores = self.get(None, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://xteam.hq.bowstreet.com/redfoot-builtin#RemoteStore")
	for rstore in rstores:
	    locationlist = self.get(rstore[0], "http://xteam.hq.bowstreet.com/redfoot-builtin#location", None)
            if len(locationlist) == 0:
                continue
            location = locationlist[0][2][1:]
            systemIDlist = self.get(rstore[0], "http://xteam.hq.bowstreet.com/redfoot-builtin#systemID", None)
            if len(systemIDlist) == 0:
                systemID = None
            else:
                systemID = systemIDlist[0][2][1:]
            
            from redfoot.storeio import StoreIO

            storeIO = StoreIO()
            storeIO.setStore(TripleStore())

            from urllib import basejoin
            storeIO.load(basejoin(self.store.location, location), systemID)
            self.connectTo(storeIO.getStore())


    def setStore(self, store):
        self.store = store
        self._preCacheRemoteStores()

    def getStore(self):
        return self.store
 
    def connectTo(self, store):
        self.stores.addStore(store)

    def get(self, subject=None, property=None, value=None):
        class Visitor:
            def __init__(self):
                self.list = []

            def callback(self, subject, property, value):
                self.list.append((subject, property, value))

        visitor = Visitor()

        self.store.visit(visitor, subject, property, value);
        self.stores.visit(visitor, subject, property, value)

	return visitor.list

    def remove(self, subject=None, property=None, value=None):
        self.store.remove(subject, property, value)

    def add(self, subject, property, value):
        self.store.add(subject, property, value)

# $Log$
# Revision 1.2  2000/10/03 22:12:57  eikeon
# Fixed up ^
#
# Revision 1.1  2000/10/03 06:01:50  jtauber
# moved MultiStore and StoreNode to rednode.py
#
