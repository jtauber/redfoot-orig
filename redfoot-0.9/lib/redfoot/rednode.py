# $Header$

from rdf.store import TripleStore
from rdf.query import QueryStore
from rdf.storeio import AutoSaveStoreIO
from rdf.const import *
from rdf.literal import literal, un_literal, is_literal

class RedNode(QueryStore):
    ""

    def __init__(self):
        pass
        
        def toRelativeURL(path):
            import sys
            from os.path import join, dirname
            from urllib import pathname2url
            libDir = dirname(sys.modules["redfoot.rednode"].__file__)
            return pathname2url(join(libDir, path))

        self.local = Local(self)
        self.neighbourhood = Neighbourhood()

        self.connectTo(toRelativeURL("rdfSchema.rdf"), "http://www.w3.org/2000/01/rdf-schema")
        self.connectTo(toRelativeURL("rdfSyntax.rdf"), "http://www.w3.org/1999/02/22-rdf-syntax-ns")
        self.connectTo(toRelativeURL("builtin.rdf"), "http://redfoot.sourceforge.net/2000/10/06/builtin")

    def visit(self, callback, subject=None, property=None, value=None):
        # todo: order?
        self.local.visit(callback, subject, property, value)
        self.neighbourhood.visit(callback, subject, property, value)

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
        self.neighbourhood.addNeighbour(store)


class Local(QueryStore, AutoSaveStoreIO):
    def __init__(self, rednode):
        # TODO: need to clean up the __init__ calling
        TripleStore.__init__(self)
        self.rednode = rednode

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
        # show classes in neighbourhood as well
        self.rednode.visit(subclass, None, SUBCLASSOF, type)
        def instance(s, p, o, processInstance=processInstance, \
                     currentDepth=currentDepth, recurse=recurse):
            processInstance(s, currentDepth, recurse)
        # only show local instances
        self.visit(instance, None, TYPE, type)

    # May need to move the following method elsewhere if we need
    # resourcesByClassV defined for all combinations and do not wish to
    # overload what it mean for Local
    def visitResourcesByType(self, processClass, processResource):
        def klass(s, p, o, processClass=processClass, processResource=processResource, self=self):
            if self.getFirst(None, TYPE, s)!=None:
                processClass(s)
            def resource(s, p, o, processClass=processClass,\
                         processResource=processResource, self=self):
                processResource(s)
            # only show local instances
            self.visit(resource, None, TYPE, s)
        # show classes in neighbourhod as well as in local store
        self.rednode.visit(klass, None, TYPE, CLASS)


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


class MultiStore(QueryStore):
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
#~ Revision 5.1  2000/12/14 05:15:26  eikeon
#~ converted to new query interface (for a second time?)
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
