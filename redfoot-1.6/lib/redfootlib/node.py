from redfootlib.util import unique_date_time as date_time
from redfootlib.util import encode_as_single_line as encode
from redfootlib.util import decode_from_single_line as decode

from redfootlib.rdf.query.schema import SchemaQuery
from redfootlib.rdf.store.triple import TripleStore
from redfootlib.rdf.store.storeio import LoadSave

from threading import RLock
from threading import Condition

class Dirty(object):
    def __init__(self):
        super(Dirty, self).__init__()
        self.dirtyBit = DirtyBit()
        
    def remove(self, subject=None, predicate=None, object=None):
        self.dirtyBit.set()
        super(Dirty, self).remove(subject, predicate, object)

    def add(self, subject, predicate, object):
        self.dirtyBit.set()
        super(Dirty, self).add(subject, predicate, object)

    def load(self, location, uri=None, create=0):
        super(Dirty, self).load(location, uri, create)
        print "Done loading '%s'" % location
        self.dirtyBit.clear() # we just loaded... therefore we are clean

#     def visit(self, callback, (subject, predicate, object)):
#         if self.dirtyBit.value()==1:
#             self.dirtyBit.clear()            
#             self.update()
#         super(Dirty, self).visit(callback, (subject, predicate, object))
            

class DirtyBit:
    def __init__(self):
        self._mon = RLock()
        self._rc = Condition(self._mon)
        self._dirty = 0
        
    def clear(self):
        self._mon.acquire()
        self._dirty = 0
        #self._rc.notify() only interested in knowing when we are dirty
        self._mon.release()

    def set(self):
        self._mon.acquire()
        self._dirty = 1
        self._rc.notify()
        self._mon.release()

    def value(self):
        return self._dirty

    def wait(self):
        self._mon.acquire()
        self._rc.wait()
        self._mon.release()

from redfootlib.rdf.objects import resource, literal
from redfootlib.rdf.const import LABEL, SUBJECT, PREDICATE, OBJECT, TYPE, RESOURCE

from redfootlib.rdf.query.functors import sort
from redfootlib.rdf.query.functors import remove_duplicates

CONTEXT = resource("http://redfoot.net/2002/05/CONTEXT")
MEANING = resource("http://redfoot.net/2002/05/MEANING")
TIMESTAMP = resource("http://redfoot.net/2002/05/TIMESTAMP")
ADD = resource("http://redfoot.net/2002/05/ADD")


class NodeStore(TripleStore, object):
    def __init__(self, node):
        super(NodeStore, self).__init__()
        self.context_id = None
        self.node = node
        
    def visit(self, callback, (subject, predicate, object)):
        self.node.update(self.context_id, self)
        return super(NodeStore, self).visit(callback, (subject, predicate, object))


class AbstractNode(Dirty, object):
    def __init__(self):
        super(AbstractNode, self).__init__()
        self.uri = "TODO"

    def _generate_id(self):
        return "%s/%s" % (self.uri, date_time())
    
    def make_statement(self, context_id, subject, predicate, object):
        statement_id = resource(self._generate_id())
        self.add(statement_id, CONTEXT, context_id)
        self.add(statement_id, MEANING, ADD)
        self.add(statement_id, TIMESTAMP, literal(date_time()))
        self.add(statement_id, SUBJECT, subject)
        self.add(statement_id, PREDICATE, predicate)
        self.add(statement_id, OBJECT, object)

    def load(self, location, uri=None, create=0):
        super(AbstractNode, self).load(location, uri, create)
        self.dirtyBit.set()
        
    def update(self, context_id, store):
        if self.dirtyBit.value()==1:
            self.dirtyBit.clear()            
            def chron((s1, p1, o1), (s2, p2, o2)):
                time_a = self.get_first_value(s1, TIMESTAMP, '')
                time_b = self.get_first_value(s2, TIMESTAMP, '')
                return cmp(str(time_a), str(time_b))
        
            def callback(s, p, o):
                subject = self.get_first_value(s, SUBJECT)
                predicate = self.get_first_value(s, PREDICATE)
                object = self.get_first_value(s, OBJECT)
                if subject and predicate and object:
                    store.add(subject, predicate, object)
            #callback = slice(callback, start, end)
            sort(chron, self.visit)(
                remove_duplicates(callback, lambda args: args[0]),
                (None, CONTEXT, context_id))
        

class Neighbours(object): 
    def __init__(self):
        super(Neighbours, self).__init__()
        self.neighbours = [] # neighbours (or their proxies)

    def add(self, s, p, o):
        super(Neighbours, self).add(s, p, o)
        for neighbour in self.neighbours:
            neighbour.add(s, p, o)

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)
        neighbour.visit(self.add, (None, None, None))
        self.visit(neighbour.add, (None, None, None))

    def remove_neighbour(self, neighbour):
        self.neighbours.remove(neighbour)
            

class ForwardProxy(object):

    def send_add(self, s, p, o):
        message = "ADD %s %s %s" % (s.n3(), p.n3(), o.n3())
        self.push(encode(message)+"\r\n")

    def visit(self, cb, (s, p, o)):
        self.push("VISIT\r\n")


class ReverseProxy(object):
    def __init__(self):
        super(ReverseProxy, self).__init__()
        self.buffer = ""
        
    def collect_incoming_data(self, data):
        self.buffer = self.buffer + data
        
    def found_terminator(self):
        data = self.buffer
        self.buffer = ""
        self.process(data)
        
    def handle_close(self):
        self.close()

    def process(self, data):
        if data[:4] == "QUIT":
            self.handle_close()
        elif data[:3] == "ADD":
            from redfootlib.rdf.objects import n3
            s, p, o = map(lambda v: n3(decode(v)), data[4:].split(" ", 2))
            self.reverse_add(s, p, o)
        elif data[:5] == "VISIT":
            s, p, o = None, None, None
            self.reverse_visit(s, p, o)
        else:
            print "Data:", data


import asynchat, socket

class Proxy(ForwardProxy, ReverseProxy, asynchat.async_chat):
    loop_thread = None
    
    def __init__(self):
        super(Proxy, self).__init__()
        
    def _run(self):
        """Run asyncore loop if not already running"""
    
        from redfootlib.server.medusaglue import _run
        from threading import Thread
        t = Thread(target = _run, args = ())
        t.setDaemon(1)
        t.start()

    def outward(self, host, port):
        asynchat.async_chat.__init__(self)
        self.set_terminator("\r\n")        
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.set_reuse_addr()
        self._run()        
        print "connection to", host, port

    def inward(self, (conn, addr)):
        self.set_terminator("\r\n")
        asynchat.async_chat.__init__(self, conn)
        self.set_reuse_addr()
        self._run()        
        print "connection from", addr


class ProxyNode(Proxy):

    def add(self, s, p, o):
        self.send_add(s, p, o)

    def reverse_add(self, s, p, o):
        self.reverse.add(s, p, o)

    def reverse_visit(self, s, p, o):
        self.reverse.visit(self.add, (s, p, o))

    def handle_close(self):
        super(ProxyNode, self).handle_close()        
        self.reverse.remove_neighbour(self)


import asyncore    
class Node(Neighbours, AbstractNode, SchemaQuery, LoadSave, TripleStore,
           asyncore.dispatcher):
    
    def add(self, s, p, o):
        if not self.exists(s, p, o):
            super(Node, self).add(s, p, o)

    def call(self, host, port):
        proxy = ProxyNode()
        proxy.reverse = self        
        proxy.outward(host, port)        
        self.add_neighbour(proxy)

    def listen_on(self, host, port):
        addr = host, port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(addr)
        self.listen(5)

    def handle_accept(self):
        proxy = ProxyNode()
        proxy.reverse = self        
        proxy.inward(self.accept())        
        self.add_neighbour(proxy)


