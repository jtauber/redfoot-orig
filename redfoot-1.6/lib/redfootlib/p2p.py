#
# $Id$

from redfootlib.set import set, DecayingSet, encode, decode


class Edge(object):
    def __init__(self):
        self.__message_set = DecayingSet(60)
        self.uids = set() # uids of interest

    def message(self, to, frm, message_id, message):
        pass

    def tell(self, to, frm, message_id, message):
        if not self.repeat(to, frm, message_id, message):
            self.message(to, frm, message_id, message)

    def knows(self):
        return self.uids

    def repeat(self, to, frm, message_id, message):
        if message_id in self.__message_set: # repeat
            return 1 # so don't send
        self.__message_set.add(message_id)
        return 0


class Neighbours(object): # requires Edge
    def __init__(self):
        super(Neighbours, self).__init__()
        self.neighbours = [] # neighbours (or their proxies)
        self.__known_cache_dirty = 1
        self.__known_cache = None

    def message(self, to, frm, message_id, message):
        for neighbour in self.neighbours:
            if to in neighbour.knows():
                neighbour.tell(to, frm, message_id, message)

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)
        self.invalidate_cache()

    def remove_neighbour(self, neighbour):
        self.neighbours.remove(neighbour)
        self.invalidate_cache()
            
    def invalidate_cache(self):
        if self.__known_cache_dirty==0:
            self.__known_cache_dirty = 1
            for neighbour in self.neighbours:
                neighbour.invalidate_cache()

    def knows(self):
        if self.__known_cache_dirty==1:
            self.__known_cache_dirty = 0
            self.__known_cache = s = set()
            for neighbour in self.neighbours:
                s += neighbour.knows()
        return super(Neighbours, self).knows() + self.__known_cache


class ForwardProxy(object):

    def send_tell(self, to, frm, message_id, message):
        message = encode(message)
        self.push("TELL %s %s %s %s\r\n" % (to, frm, message_id, message))

    def send_who(self):
        self.push("WHO\r\n")

    def send_known(self):
        list = " ".join(self.knows())
        self.push("KNOWN %s\r\n" % list)
        

class ReverseProxy(object):
    def __init__(self):
        super(ReverseProxy, self).__init__()
        self.buffer = ""
        self._knows = set()
        
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
        elif data[:3] == "WHO":            
            self.send_known()
        elif data[:4] == "TELL":
            args = data[5:].split(" ", 3)
            destination = args[0]
            source = args[1]
            message_id = args[2]
            message = decode(args[3])
            self.tell(destination, source, message_id, message)
        elif data[:5] == "KNOWN":
            self._knows = set(data[6:].split(" "))
            self.invalidate_cache()
        else:
            print "Data:", data

            
import asynchat, socket

class Proxy(ForwardProxy, ReverseProxy, asynchat.async_chat):
    def __init__(self):
        super(Proxy, self).__init__()
        
    def message(self, to, frm, message_id, message):
        if to in self.knows():
            self.send_tell(to, frm, message_id, message)
        super(Proxy, self).message(to, frm, message_id, message)

    def knows(self):
        return self._knows + super(Proxy, self).knows()
    
    def outward(self, host, port):
        asynchat.async_chat.__init__(self)
        self.set_terminator("\r\n")        
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self.set_reuse_addr()                
        self.send_who()
        self.send_known()
        print "connection to", host, port

    def inward(self, (conn, addr)):
        self.set_terminator("\r\n")
        asynchat.async_chat.__init__(self, conn)
        self.set_reuse_addr()        
        self.send_who()
        self.send_known()
        print "connection from", addr


class ProxyNode(Proxy, Neighbours, Edge):
    def add_neighbour(self, neighbour):
        super(ProxyNode, self).add_neighbour(neighbour)
        self.send_who()
        self.send_known()
    
    def handle_close(self):
        super(ProxyNode, self).close()        
        for neighbour in self.neighbours:
            neighbour.remove_neighbour(self)
        

import asyncore

class Node(Neighbours, Edge, asyncore.dispatcher):

    def call(self, host, port):
        proxy = ProxyNode()
        proxy.outward(host, port)        
        proxy.add_neighbour(self)
        self.add_neighbour(proxy)


    def listen_on(self, addr):        
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(addr)
        self.listen(5)

    def handle_accept(self):
        proxy = ProxyNode()
        proxy.inward(self.accept())        
        proxy.add_neighbour(self)
        self.add_neighbour(proxy)        


class Cache(object):
    def __init__(self):
        super(Cache, self).__init__()
        self.message_set = []
        self.last_message = {}

    def repeat(self, to, frm, message_id, message):
        msg = (to, frm, message_id, message)
        if msg in self.message_set: 
            return 1
        self.message_set.append(msg)
        return 0

    def add_neighbour(self, neighbour):
        super(Cache, self).add_neighbour(neighbour)
        self._backlog(neighbour, 0)

    def _backlog(self, neighbour, tell=1):
        known = neighbour.knows()        
        message_set = self.message_set
        #msg = self.last_message.setdefault(connection.remote_uid, None)
        msg = None
        if msg:
            start = message_set.index(msg) + 1
        else:
            start = 0
        for i in xrange(start, len(message_set)):
            msg = to, frm, message_id, message = message_set[i]
            if to in known:
                neighbour.message(to, frm, message_id, message)
            else:
                print "Nope:", msg
        #self.last_message[neighbour] = msg
