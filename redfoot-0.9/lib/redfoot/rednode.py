# $Header$

from rdf.store import TripleStore
from rdf.query import QueryStore
from rdf.storeio import StoreIO
from rdf.storeio import AutoSaveStoreIO
from rdf.const import *
from rdf.literal import literal, un_literal, is_literal

class RedNode(StoreIO, QueryStore):
    # local in the context of neighbours where applicable else entire
    # neighbourhood. For example, visitResourcesByType will visit
    # resoruces in the local store, but will display relevant class
    # information from the entire neighbourhood.
    
    ""

    def __init__(self):
        StoreIO.__init__(self)
        def toRelativeURL(path):
            import sys
            from os.path import join, dirname
            from urllib import pathname2url
            libDir = dirname(sys.modules["redfoot.rednode"].__file__)
            return pathname2url(join(libDir, path))

        self.local = Local() # local only
        self.neighbours = Neighbourhood() # neighbours only

        self.neighbourhood = MultiStore() # local plus neighbours
        self.neighbourhood.addStore(self.local)
        self.neighbourhood.addStore(self.neighbours)

        self.connectTo(toRelativeURL("rdfSchema.rdf"), "http://www.w3.org/2000/01/rdf-schema")
        self.connectTo(toRelativeURL("rdfSyntax.rdf"), "http://www.w3.org/1999/02/22-rdf-syntax-ns")
        self.connectTo(toRelativeURL("builtin.rdf"), "http://redfoot.sourceforge.net/2000/10/06/builtin")

    def visit(self, callback, subject=None, property=None, value=None):
        # TODO: order?
        # TODO: Fix the following in regaurds to getFirst
        self.local.visit(callback, subject, property, value)
        self.neighbours.visit(callback, subject, property, value)

    # TODO: when to call... used to call on setStore()
    def _preCacheNeighbourStores(self, baseDirectory=None):
        rstores = self.get(None, TYPE, "http://redfoot.sourceforge.net/2000/12/redfoot-builtin#Neighbour")
	for rstore in rstores:
            location = self.getFirst(rstore[0], "http://redfoot.sourceforge.net/2000/12/redfoot-builtin#location", None)
            if location!=None:
                systemID = self.getFirst(rstore[0], "http://redfoot.sourceforge.net/2000/12/redfoot-builtin#systemID", None)
                if systemID!=None:
                    systemID = un_literal(systemID)

                from urllib import basejoin
                self.connectTo(basejoin(self.location, location), systemID)
            else:
                pass # no location to connect to

    def connectTo(self, location, URI=None):
        if URI==None:
            URI=location

        from rdf.storeio import TripleStoreIO

        storeIO = TripleStoreIO()        
        storeIO.load(location, URI)
        self._connectTo(storeIO)

    def _connectTo(self, store):
        self.neighbours.addNeighbour(store)

    # May need to move the following method elsewhere if we need
    # subClassV defined for all combinations and do not wish to
    # overload what it mean for Local
    def visitSubclasses(self, processClass, processInstance, type, currentDepth=0, recurse=1):
        processClass(type, currentDepth, recurse)
        def subclass(s, p, o, self=self, currentDepth=currentDepth, recurse=recurse,\
                     processClass=processClass, processInstance=processInstance):
            if recurse:
                self.visitSubclasses(processClass, processInstance, s, currentDepth+1)
            else:
                processClass(s, currentDepth+1, recurse)
        # show classes in neighbours as well
        self.neighbourhood.visit(subclass, None, SUBCLASSOF, type)
        def instance(s, p, o, processInstance=processInstance, \
                     currentDepth=currentDepth, recurse=recurse):
            processInstance(s, currentDepth, recurse)
        # only show local instances
        self.local.visit(instance, None, TYPE, type)

    # May need to move the following method elsewhere if we need
    # resourcesByClassV defined for all combinations and do not wish to
    # overload what it mean for Local
    def visitResourcesByType_original(self, processClass, processResource):
        def klass(s, p, o, processClass=processClass, processResource=processResource, self=self):
            if self.local.getFirst(None, TYPE, s)!=None:
                processClass(s)
            def resource(s, p, o, processClass=processClass,\
                         processResource=processResource, self=self):
                processResource(s)
            # only show local instances
            self.local.visit(resource, None, TYPE, s)
        # show classes in neighbourhod as well as in local store
        self.neighbourhood.visit(klass, None, TYPE, CLASS)

    def visitResourcesByType(self, processClass, processResource):
        from rdf.query import ObjectSetBuilder
        setBuilder = ObjectSetBuilder()
        self.neighbourhood.query(setBuilder, None, TYPE, None)
        types = setBuilder.set.keys()
        for klass in types:
            if self.local.getFirst(None, TYPE, klass)!=None:
                processClass(klass)
                def resource(s, p, o, processClass=processClass,\
                             processResource=processResource, self=self):
                    processResource(s)
                # only show local instances
                self.local.visit(resource, None, TYPE, klass)


    def output(self, stream, URI=None, subject=None, predicate=None, object=None):
        self.local.output(stream, URI, subject, predicate, object)

    def getTypelessResources(self):
        return self.local.getTypelessResources()


class Local(QueryStore, AutoSaveStoreIO):
    def __init__(self):
        # TODO: need to clean up the __init__ calling
        AutoSaveStoreIO.__init__(self)


class Neighbourhood(QueryStore):
    # could this also be a subclass instead of a wrapper?
    def __init__(self):
        self.stores = MultiStore()

    def addNeighbour(self, store):
        self.stores.addStore(store)

    def add(self, subject, predicate, object):
        raise "Can not write to Neighbourhood store!"

    def visit(self, callback, subject=None, property=None, value=None):
        self.stores.visit(callback, subject, property, value)

    def remove(self, subject=None, predicate=None, object=None):
        raise "Can not remove from Neighbourhood store!"


class MultiStore(StoreIO, QueryStore):
    ""
    
    def __init__(self):
        StoreIO.__init__(self)
        self.stores = {}

    def addStore(self, store):
        self.stores[store] = 1

    def getStores(self):
        return self.stores.keys()

    def visit(self, callback, subject=None, property=None, value=None):
        for store in self.getStores():
            store.visit(callback, subject, property, value)


#~ $Log$
#~ Revision 5.4  2000/12/19 06:11:09  eikeon
#~ added method to override getTypelessResources to only pay attention to local resources
#~
#~ Revision 5.3  2000/12/19 06:04:04  eikeon
#~ Moved the 'local in context of neighbourhood' methods to RedNode... else we where overriding the corresponding methods on local, which someone may care about
#~
#~ Revision 5.2  2000/12/17 23:41:58  eikeon
#~ removed of log messages
#~
#~ Revision 5.1  2000/12/14 05:15:26  eikeon
#~ converted to new query interface (for a second time?)
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
