from __future__ import generators

from redfootlib.util import unique_date_time as date_time
from redfootlib.util import encode_as_single_line as encode
from redfootlib.util import decode_from_single_line as decode

from redfootlib.rdf.triple_store import TripleStore

from threading import RLock
from threading import Condition

def _run():
    """Run asyncore loop if not already running"""
    
    from redfootlib.server.medusaglue import _run
    from threading import Thread
    t = Thread(target = _run, args = ())
    t.setDaemon(1)
    t.start()

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

from redfootlib.rdf.nodes import URIRef, Literal
from redfootlib.rdf.const import LABEL, SUBJECT, PREDICATE, OBJECT, TYPE, RESOURCE

#from redfootlib.rdf.query.functors import sort
#from redfootlib.rdf.query.functors import remove_duplicates

CONTEXT = URIRef("http://redfoot.net/2002/05/CONTEXT")
MEANING = URIRef("http://redfoot.net/2002/05/MEANING")
TIMESTAMP = URIRef("http://redfoot.net/2002/05/TIMESTAMP")
ADD = URIRef("http://redfoot.net/2002/05/ADD")
REMOVE = URIRef("http://redfoot.net/2002/05/REMOVE")


class NodeStore(TripleStore, object):
    def __init__(self, node):
        super(NodeStore, self).__init__()
        self.context_id = None
        self.node = node
        
    def triples(self, s, p, o):
        self.node.update(self.context_id, self)
        for triple in super(NodeStore, self).triples(s, p, o):
            yield triple
        

class AbstractNode(object):
    def __init__(self):
        super(AbstractNode, self).__init__()
        self.uri = "TODO"
        self.dirtyBit = DirtyBit()
        
    def add(self, subject, predicate, object):
        self.dirtyBit.set()
        super(AbstractNode, self).add(subject, predicate, object)

    def remove(self, subject=None, predicate=None, object=None):
        self.dirtyBit.set()
        super(AbstractNode, self).remove(subject, predicate, object)

    def _generate_id(self):
        return "%s/%s" % (self.uri, date_time())
    
    def make_statement(self, context_id, subject, predicate, object):
        statement_id = URIRef(self._generate_id())
        self.add(statement_id, CONTEXT, context_id)
        self.add(statement_id, MEANING, ADD)
        self.add(statement_id, TIMESTAMP, Literal(date_time()))
        self.add(statement_id, SUBJECT, subject)
        self.add(statement_id, PREDICATE, predicate)
        self.add(statement_id, OBJECT, object)

    def retract_statement(self, context_id, subject, predicate, object):
        statement_id = URIRef(self._generate_id())
        self.add(statement_id, CONTEXT, context_id)
        self.add(statement_id, MEANING, REMOVE)
        self.add(statement_id, TIMESTAMP, Literal(date_time()))
        subject = subject or Literal("ANY")
        predicate = predicate or Literal("ANY")
        object = object or Literal("ANY")        
        self.add(statement_id, SUBJECT, subject)
        self.add(statement_id, PREDICATE, predicate)
        self.add(statement_id, OBJECT, object)

    def load(self, location, uri=None, create=0):
        super(AbstractNode, self).load(location, uri, create)
        self.dirtyBit.set()
        
    def update(self, context_id, store):
        if self.dirtyBit.value()==1:
            self.dirtyBit.clear()            
            def chron(s1, s2):
                time_a = self.first_object(s1, TIMESTAMP) or ''
                time_b = self.first_object(s2, TIMESTAMP) or ''
                return cmp(str(time_a), str(time_b))
        
            def callback(s):
                subject = self.first_object(s, SUBJECT)
                predicate = self.first_object(s, PREDICATE)
                object = self.first_object(s, OBJECT)
                if subject and predicate and object:
                    meaning = self.first_object(s, MEANING) or None
                    if meaning==ADD:
                        store.add(subject, predicate, object)
                    elif meaning==REMOVE:
                        if subject==Literal("ANY"):
                            subject = None
                        if predicate==Literal("ANY"):
                            predicate = None
                        if object==Literal("ANY"):
                            object = None
                        store.remove(subject, predicate, object)
            #callback = slice(callback, start, end)
            subjects = list(self.subjects(CONTEXT, context_id))
            # TODO: remove duplicates?
            subjects.sort(chron)
            for subject in subjects:
                callback(subject)
#             sort(chron, self.visit)(
#                 remove_duplicates(callback, lambda args: args[0]),
#                 (None, CONTEXT, context_id))
        

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
        for s, p, o in neighbour:
            self.add(s, p, o)
        for s, p, o in self:
            neighbour.add(s, p, o)

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
    
    def __init__(self):
        super(Proxy, self).__init__()
        
    def outward(self, host, port):
        asynchat.async_chat.__init__(self)
        self.set_terminator("\r\n")        
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.set_reuse_addr()
        _run()        
        print "connection to", host, port

    def inward(self, (conn, addr)):
        self.set_terminator("\r\n")
        asynchat.async_chat.__init__(self, conn)
        self.set_reuse_addr()
        _run()        
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
class Node(Neighbours, AbstractNode, TripleStore,
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
        print "listening on '%s:%s'" % (host, port)
        addr = host, port
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(addr)
        self.listen(5)
        _run()

    def handle_accept(self):
        proxy = ProxyNode()
        proxy.reverse = self        
        proxy.inward(self.accept())        
        self.add_neighbour(proxy)



