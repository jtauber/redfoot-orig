# $Header$

from rdf.store import TripleStore
from rdf.query import QueryStore
from rdf.storeio import StoreIO

class RedNode(QueryStore, StoreIO, TripleStore):
    ""

    def __init__(self):
        TripleStore.__init__(self)
        
        def toRelativeURL(path):
            import sys
            from os.path import join, dirname
            from urllib import pathname2url
            libDir = dirname(sys.modules["redfoot.rednode"].__file__)
            return pathname2url(join(libDir, path))

        self.neighbourhood = Neighbourhood(self)

        self.connectTo(toRelativeURL("rdfSchema.rdf"), "http://www.w3.org/2000/01/rdf-schema")
        self.connectTo(toRelativeURL("rdfSyntax.rdf"), "http://www.w3.org/1999/02/22-rdf-syntax-ns")
        self.connectTo(toRelativeURL("builtin.rdf"), "http://redfoot.sourceforge.net/2000/10/06/builtin")

    # TODO: when to call... used to call on setStore()
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

    def connectTo(self, location, URI=None):
        if URI==None:
            URI=location

        from rdf.storeio import TripleStoreIO

        storeIO = TripleStoreIO()        
        storeIO.load(location, URI)
        self._connectTo(storeIO)

    def _connectTo(self, store):
        self.neighbourhood.addNeighbour(store)


from rdf.literal import literal, un_literal, is_literal

class Neighbourhood:
    # could this also be a subclass instead of a wrapper?
    def __init__(self, rednode):
        self.rednode = rednode
        self.stores = MultiStore()

    def addNeighbour(self, store):
        self.stores.addStore(store)

    def visit(self, callback, subject=None, property=None, value=None):
        self.rednode.visit(callback, subject, property, value);
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

    def label(self, subject, default=None):
        list = []
        def callback(subject, property, value, list=list):
            list.append((subject, property, value))
            return 0 # tell the visitor to stop
        
        self.visit(callback, subject, QueryStore.LABEL, None)

        if len(list) > 0:
            return un_literal(list[0][2])     # TODO: currently only returns first label
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

    def propertyValuesV(self, subject, processPropertyValue):
        def callbackAdaptor(s, p, o, processPropertyValue=processPropertyValue):
            processPropertyValue(p, o)
        self.stores.visit(callbackAdaptor, subject, None, None)
        
    def transitiveSuperTypes(self, type):
        set = {}
        set[type] = 1

        for subclassStatement in self.get(type, QueryStore.SUBCLASSOF, None):
            for item in self.transitiveSuperTypes(subclassStatement[2]):
                set[item] = 1

        return set.keys()

    def transitiveSubTypes(self, type):
        set = {}
        set[type] = 1

        for subclassStatement in self.get(None, QueryStore.SUBCLASSOF, type):
            for item in self.transitiveSubTypes(subclassStatement[0]):
                set[item] = 1

        return set.keys()

    # callback may be called more than once for the same possibleValue... user
    # of this method will have to remove duplicates
    def getPossibleValuesV(self, property, possibleValue):        
        def rangeitem(s, p, o, self=self, possibleValue=possibleValue):
            for type in self.transitiveSubTypes(o):
                self.visit(possibleValue, None, QueryStore.TYPE, type)

        self.visit(rangeitem, property, QueryStore.RANGE, None)

            
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
        

#~ $Log$
#~ Revision 4.5  2000/12/05 00:02:25  eikeon
#~ fixing some of the local / neighbourhood stuff
#~
#~ Revision 4.4  2000/12/04 22:49:10  eikeon
#~ refactored *All methods into Neighbourhood class
#~
#~ Revision 4.3  2000/12/04 22:07:35  eikeon
#~ got rid of all the getStore().getStore() stuff by using Multiple inheritance and mixin classes instead of all the classes being wrapper classes
#~
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
