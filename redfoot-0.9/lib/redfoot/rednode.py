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
        
        

from rdf.query import QueryStore
from rdf.storeio import StoreIO

class StoreNode(QueryStore, StoreIO, TripleStore):
    ""

    class Neighbourhood:
        # could this also be a subclass instead of a wrapper?
        def __init__(self, rednode):
            self.rednode = rednode

        def visit(self, callback, subject=None, property=None, value=None):
            self.rednode.visit(callback, subject, property, value);
            self.rednode.stores.visit(callback, subject, property, value)


        def get(self, subject=None, property=None, value=None):
            class Visitor:
                def __init__(self):
                    self.rednode.list = []

                def callback(self, subject, property, value):
                    self.rednode.list.append((subject, property, value))

            visitor = Visitor()
            self.visit(visitor.callback, subject, property, value);
            return visitor.list

        def label(self, subject, default=None):
            l = self.get(subject, QueryStore.LABEL, None)

            if len(l) > 0:
                return l[0][2][1:]     # TODO: currently only returns first label
            else:
                return subject

        # TODO: move rednode specific queries to a rednode wrapper class

        def resourcesByClassV(self, processClass, processResource):
            from rdf.query import QueryStore
            for klass in self.get(None, QueryStore.TYPE, QueryStore.CLASS):
                first = 1
                for resource in self.get(None, QueryStore.TYPE, klass[0]):
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
                    self.rednode.store = store
                    self.rednode.processClass = processClass
                    self.rednode.processResource = processResource

                def callback(self, subject, property, value):
                    self.rednode.processClass(subject)

                    class Visitor:
                        def __init__(self, processResource):
                            self.rednode.processResource = processResource

                        def callback(self, subject, property, value):
                            self.rednode.processResource(subject)

                    visitor = Visitor(self.rednode.processResource)

                    from rdf.query import QueryStore
                    self.visit(visitor.callback, None, QueryStore.TYPE, subject)

            visitor = Visitor(self.rednode.store, processClass, processResource)

            from rdf.query import QueryStore
            self.visit(visitor.callback, None, QueryStore.TYPE, QueryStore.CLASS)


        def subClassV(self, type, processClass, processInstance, currentDepth=0, recurse=1):
            from rdf.query import QueryStore
            processClass(type, currentDepth, recurse)
            for subclassStatement in self.get(None, QueryStore.SUBCLASSOF, type):
                if recurse:
                    self.rednode.subClassV(subclassStatement[0], processClass, processInstance, currentDepth+1)
                else:
                    processClass(subclassStatement[0], currentDepth+1, recurse)
            for instanceStatement in self.get(None, QueryStore.TYPE, type):
                processInstance(instanceStatement[0], currentDepth, recurse)


    def __init__(self):
        TripleStore.__init__(self)
        
        def toRelativeURL(path):
            import sys
            from os.path import join, dirname
            from urllib import pathname2url
            libDir = dirname(sys.modules["redfoot.rednode"].__file__)
            return pathname2url(join(libDir, path))

        self.neighbourhood = Neighbourhood(self)
        self.stores = MultiStore()

        self.connectTo(toRelativeURL("rdfSchema.rdf"), "http://www.w3.org/2000/01/rdf-schema")
        self.connectTo(toRelativeURL("rdfSyntax.rdf"), "http://www.w3.org/1999/02/22-rdf-syntax-ns")
        self.connectTo(toRelativeURL("builtin.rdf"), "http://redfoot.sourceforge.net/2000/10/06/builtin")

    def _preCacheRemoteStores(self, baseDirectory=None):
        rstores = self.neighbourhood.get(None, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://redfoot.sourceforge.net/2000/10/06/builtin#RemoteStore")
	for rstore in rstores:
	    locationlist = self.neighbourhood.get(rstore[0], "http://xteam.hq.bowstreet.com/redfoot-builtin#location", None)
            if len(locationlist) == 0:
                continue
            location = locationlist[0][2][1:]
            systemIDlist = self.neighbourhood.get(rstore[0], "http://xteam.hq.bowstreet.com/redfoot-builtin#systemID", None)
            if len(systemIDlist) == 0:
                systemID = None
            else:
                systemID = systemIDlist[0][2][1:]

            from urllib import basejoin
            self.connectTo(basejoin(self.location, location), systemID)

#    def setStore(self, store):
#        self.store = store
#        self._preCacheRemoteStores()

#    def getStore(self):
#        return self.store

    def connectTo(self, location, URI=None):
        if URI==None:
            URI=location

        from rdf.storeio import TripleStoreIO

        #storeIO = StoreIO(TripleStore())
        storeIO = TripleStoreIO()        
        storeIO.load(location, URI)
        self._connectTo(storeIO)

    def _connectTo(self, store):
        self.stores.addStore(store)

#~ $Log$
#~ Revision 4.2  2000/12/04 22:00:59  eikeon
#~ got rid of all the getStore().getStore() stuff by using Multiple inheritance and mixin classes instead of all the classes being wrapper classes
#~
#~ Revision 4.1  2000/12/04 01:26:44  eikeon
#~ no more getStore() on StoreIO
#~
#~ Revision 4.0  2000/11/06 15:57:34  eikeon
#~ VERSION 4.0
#~
#~ Revision 3.1  2000/11/02 21:48:27  eikeon
#~ removed old log messages
#~
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
