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

        visitor = Visitor()

        self.visit(visitor, subject, property, value)
        
	return visitor.list
        
        
class StoreNode:
    ""

    def __init__(self):
        self.stores = MultiStore()

        self.connectTo("tests/rdfSchema.rdf", "http://www.w3.org/2000/01/rdf-schema")
        self.connectTo("tests/rdfSyntax.rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns")
        self.connectTo("builtin.rdf", "http://redfoot.sourceforge.net/2000/10/06/builtin")

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

            from urllib import basejoin
            self.connectTo(basejoin(self.store.location, location), systemID)

    def setStore(self, store):
        self.store = store
        self._preCacheRemoteStores()

    def getStore(self):
        return self.store

    def connectTo(self, location, URI=None):
        if URI==None:
            URI=location

        from redfoot.storeio import StoreIO

        storeIO = StoreIO()
        storeIO.setStore(TripleStore())
        storeIO.load(location, URI)
        self._connectTo(storeIO.getStore())

    def _connectTo(self, store):
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
# Revision 1.5  2000/10/08 05:46:32  jtauber
# refactored creation and use of storeIO for connectTo into own method
#
# Revision 1.4  2000/10/07 02:19:03  jtauber
# rednode now loads in builtin.rdf
#
# Revision 1.3  2000/10/05 00:58:50  jtauber
# added remove and add methods which just call the corresponding methods on the store
#
# Revision 1.2  2000/10/03 22:12:57  eikeon
# Fixed up ^
#
# Revision 1.1  2000/10/03 06:01:50  jtauber
# moved MultiStore and StoreNode to rednode.py
#
