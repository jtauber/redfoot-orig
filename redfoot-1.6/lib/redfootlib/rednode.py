
from rdflib.triple_store import TripleStore
from rdflib.store.neighbourhood import Neighbourhood
from rdflib.store.composite import CompositeStore
from rdflib.store.autosave import AutoSave
from redfootlib.neighbour_manager import NeighbourManager
from rdflib.model.schema import Schema
from redfootlib import rdf_files

from redfootlib.node import NodeStore, Node

from rdflib.nodes import URIRef

from redfootlib.rdf.query.visit import Visit

LISTEN_ON = URIRef("http://redfoot.net/2002/05/listen_on")
ADDRESS = URIRef("http://redfoot.net/2002/05/Address")
HOST = URIRef("http://redfoot.net/2002/05/host")
PORT = URIRef("http://redfoot.net/2002/05/port")

SERVER = URIRef("http://redfoot.net/2002/05/server")
APP = URIRef("http://redfoot.net/2002/05/app")
APP_CLASS = URIRef("http://redfoot.net/2002/05/app_class")

sn = 0

class RedNode(Visit, NeighbourManager, AutoSave, TripleStore):
    """
    A RedNode is a store that is queryable via high level queries, can
    manage its neighbour connections, [automatically] save to RDF/XML
    syntax, and load from RDF/XML syntax.

    A RedNode contains a neighbourhood store for querying the nodes'
    entire neighbourhood, which includes itself and its neighbours in
    that order.
    """

    def __init__(self):
        super(RedNode, self).__init__()
        neighbours = Neighbours()
        neighbours.append_store(rdf_files.schema)
        neighbours.append_store(rdf_files.syntax)
        neighbours.append_store(rdf_files.builtin)
        self.neighbourhood = RedNeighbourhood(self, neighbours)
        self.neighbours = neighbours

        self.uri = None
        self.node = Node()
        self.node_store = NodeStore(self.node)
        filename, uri = "node.rdf", "http://redfoot.net/2002/05/11/"
        self.node.load(filename, uri, 1)
        self.neighbours.append_store(self.node_store)

    def __get_uri(self):
        if not self.__uri:
            from socket import getfqdn
            self.__uri = "http://%s/" % getfqdn()
            print "WARNING: rednode has no uri... using computed value of '%s'" % self.__uri
        return self.__uri

    def __set_uri(self, value):
        self.__uri = value

    uri = property(__get_uri, __set_uri)
    
    def make_statement(self, context_uri):
        return lambda s, p, o: self.node.make_statement(URIRef(context_uri), s, p, o)

    def retract_statement(self, context_uri):
        return lambda s, p, o: self.node.retract_statement(URIRef(context_uri), s, p, o)

    def load(self, location, uri=None, create=0):
        super(RedNode, self).load(location, uri, create)
        
        def _listen_on(o):
            host = self.get_first_value(o, HOST, None)
            port = self.get_first_value(o, PORT, None)
            if host or host=='' and port:
                self.node.listen_on(host, int(port))
        for object in self.objects(URIRef(uri), LISTEN_ON):
            _listen_on(object)
                
        def _server(o):
            host = self.get_first_value(o, HOST, None)
            port = self.get_first_value(o, PORT, None)
            if host or host=='' and port:
                from redfootlib.server import RedServer                
                server = RedServer(host, int(port))
                server.run(background=1)
                def _add_app(o):
                    app_class = self.get_first_value(o, APP_CLASS, None)
                    if app_class:
                        app = self.get_app_instance(app_class)
                        server.add_app(app)
                for object in self.objects(o, APP):
                    _add_app(object)
        for object in self.objects(URIRef(uri), SERVER):
            _server(object)

    def save(self, location=None, uri=None):
        super(RedNode, self).save(location, uri)
        print "Saving node_store..."
        self.node.save()
        print "done."


    def get_app_instance(self, name):
        names = name.split(".")
        if len(names)==2:
            package, name = ".".join(names[:-1]), names[-1]
            locals = globals = self.context.__dict__            
            module = __import__(package, globals, locals)
            AppClass = eval(name, module.__dict__)            
        else:
            print "usage: package_name.app_name"

        app = AppClass(self)
        return app

    def get_module(self, uri):
        uri = URIRef(uri)
        from redfootlib.module_store import MODULE
        value = self.neighbourhood.first_object(uri, MODULE)
        if value:
            return self._exec_module(value)
        else:
            return self.load_module(uri)

    def load_module(self, uri):
        uri = URIRef(uri)
        from redfootlib.module_store import MODULE        
        from urllib import urlopen

        from rdflib.nodes import URIRef, Literal

        from rdflib.const import LABEL, RESOURCE
        from rdflib.const import TYPE, CLASS, SUBCLASSOF
        from rdflib.const import PROPERTY, DOMAIN, RANGE

        MODULE = URIRef("http://redfoot.net/2002/05/20/module")
        MODULE_CLASS = URIRef("http://redfoot.net/2002/05/20/Module")
        
        f = urlopen(uri)
        value = f.read()
        value = "\n".join(value.split("\r\n")) # TODO: is there a better way?

        self.add(uri, MODULE, Literal(value))
        self.add(uri, TYPE, MODULE_CLASS)
        return self._exec_module(value)
        
    def _exec_module(self, value):
        if value:
            filename = "<%s MODULE>" % uri
            from new import module

            #m = module("_".join(uri.split(" ")))
            global sn
            sn += 1
            m = module("foo%s" % sn)
            try:
                code = compile(value, filename, "exec")
                import sys
                g = globals()
                g = sys.modules['__main__'].__dict__
                g = m.__dict__
                l = m.__dict__                        
                exec code in g, l
            except:
                import sys
                from traceback import print_exc, tb_lineno, extract_tb
                print_exc()
                try:
                    etype, value, tb = sys.exc_info()
                    if etype is SyntaxError:                    
                        msg, (fn, lineno, offset, line) = value
                        filename = fn or filename
                        print "Error: %s:%s:" % (filename, lineno)
                except:
                    pass
        else:
            raise "'%s' Not found" % uri
        return m
    


class Neighbours(Visit, Schema, CompositeStore):
    """
    A store of the neighbours that is queryable via high level
    queries.
    """


class RedNeighbourhood(Visit, Schema, Neighbourhood):
    """
    A store of the neighbourhood that is queryable via high level
    queries.
    
    A Neighbourhood is a store that contains a local store and a store
    of neighbours in which the local store gets visited first and then
    the neighbours in order that they where added.
    """


