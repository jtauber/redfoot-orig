# $Header$

from rdf.store import TripleStore

class MultiStore:
    ""
    
    def __init__(self):
        self.stores = {}

    def addStore(self, store):
        self.stores[store] = 1

    def getStores(self):
        return self.stores.keys()

    def visit(self, callback, subject=None, property=None, value=None):
        for store in self.getStores():
            store.visit(callback, subject, property, value)

    def get(self, subject=None, property=None, value=None):
        class Visitor:
            def __init__(self):
                self.list = []

            def callback(self, subject, property, value):
                self.list.append((subject, property, value))

        visitor = Visitor()

        self.visit(visitor.callback, subject, property, value)
        
	return visitor.list
        
        
class StoreNode:
    ""

    def __init__(self):
        def toRelativeURL(path):
            import sys
            from os.path import join, dirname
            from urllib import pathname2url
            libDir = dirname(sys.modules["redfoot.rednode"].__file__)
            return pathname2url(join(libDir, path))

        self.stores = MultiStore()

        self.connectTo(toRelativeURL("rdfSchema.rdf"), "http://www.w3.org/2000/01/rdf-schema")
        self.connectTo(toRelativeURL("rdfSyntax.rdf"), "http://www.w3.org/1999/02/22-rdf-syntax-ns")
        self.connectTo(toRelativeURL("builtin.rdf"), "http://redfoot.sourceforge.net/2000/10/06/builtin")

    def _preCacheRemoteStores(self, baseDirectory=None):
        rstores = self.get(None, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://redfoot.sourceforge.net/2000/10/06/builtin#RemoteStore")
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

        from rdf.storeio import StoreIO

        storeIO = StoreIO()
        storeIO.setStore(TripleStore())
        storeIO.load(location, URI)
        self._connectTo(storeIO.getStore())

    def _connectTo(self, store):
        self.stores.addStore(store)

    def visit(self, callback, subject=None, property=None, value=None):
        self.store.visit(callback, subject, property, value);
        self.stores.visit(callback, subject, property, value)
        

    def get(self, subject=None, property=None, value=None):
        class Visitor:
            def __init__(self):
                self.list = []

            def callback(self, subject, property, value):
                self.list.append((subject, property, value))

        visitor = Visitor()
        self.visit(visitor.callback, subject, property, value);
	return visitor.list

    def remove(self, subject=None, property=None, value=None):
        self.store.remove(subject, property, value)

    def add(self, subject, property, value):
        self.store.add(subject, property, value)


    # TODO: move rednode specific queries to a rednode wrapper class

    def resourcesByClassV(self, processClass, processResource):
        from rdf.query import QueryStore
        for klass in self.get(None, QueryStore.TYPE, QueryStore.CLASS):
            first = 1
            for resource in self.store.get(None, QueryStore.TYPE, klass[0]):
                if first:
                    processClass(klass[0])
                    first = 0
                processResource(resource[0])


    # Or for the adventurous :)
    # but note, this one will call processClass even for classes with no
    # instances unlike resourcesByClassV)
    def resourcesByClassVV(self, processClass, processResource):
        class Visitor:
            def __init__(self, store, processClass, processResource):
                self.store = store
                self.processClass = processClass
                self.processResource = processResource
            
            def callback(self, subject, property, value):
                self.processClass(subject)

                class Visitor:
                    def __init__(self, processResource):
                        self.processResource = processResource

                    def callback(self, subject, property, value):
                        self.processResource(subject)

                visitor = Visitor(self.processResource)

                from rdf.query import QueryStore
                self.store.visit(visitor.callback, None, QueryStore.TYPE, subject)

        visitor = Visitor(self.store, processClass, processResource)

        from rdf.query import QueryStore
        self.visit(visitor.callback, None, QueryStore.TYPE, QueryStore.CLASS)


    def subClassV(self, type, processClass, processInstance, currentDepth=0, recurse=1):
        from rdf.query import QueryStore
        processClass(type, currentDepth, recurse)
        for subclassStatement in self.get(None, QueryStore.SUBCLASSOF, type):
            if recurse:
                self.subClassV(subclassStatement[0], processClass, processInstance, currentDepth+1)
            else:
                processClass(subclassStatement[0], currentDepth+1, recurse)
        for instanceStatement in self.store.get(None, QueryStore.TYPE, type):
            processInstance(instanceStatement[0], currentDepth, recurse)

#~ $Log$
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
