#
# $Id$
#
#### DOCUMENTATION
#
# @@@ Main doc still to do
#
### HOW TO COMMUNICATE WITH NODE BY METHOD-CALL RATHER THAN SOCKET
#
# Call node.register(my_id, edge_object) to register with given my_id.
#
# TELL with
#   message_id = node.get_message_id()
#   node.tell(to_id, my_id, message_id, message)
# 
# Any messages the node receives addressed to you will result in a call to
#   edge_object.send_says(to_id, from_id, message_id, message)
#
# Call node.deregister(id, edge_object) or node.deregister_all(edge_object)
# when you are finished.
#
# Other methods you can call on node:
#   node.who
#   node.can_proxy
#   node.call
#   node.refresh
#
# see the doc on those methods for details
#
# Other methods edge_object may have to support:
#   edge_object.send_connected()
#     indication that node.who may have to be called to get a new list of
#     known nodes
#   edge_object.send_who()
#     request for a list of who edge_object is connected to - can be ignored
#   edge_object.send_pass_on(to_id, from_id, message_id, message)
#     will only occur if node.can_proxy has been called registering the
#     edge_object as a proxy. If that is the case, this method will be called
#     if the edge_object is being requested to pass on a message


#### IMPORTS

import asynchat
import asyncore
import socket
import sys

#### GENERIC SET DATA STRUCTURE

class set:

    def __init__(self, list=[]):
        self.__d = {}
        for item in list:
            self.__d[item] = 1

    def __add__(self, obj):
        d = []
        d.extend(self.__d)
        if obj.__class__ == set:
            d.extend(obj.__d.keys())
        else:
            d.append(obj)
        return set(d)

    __or__ = __add__

    def __sub__(self, obj):
        d = self.__d.keys()
        if obj.__class__ == set:
            for item in obj:
                if item in d:
                    d.remove(item)
        else:
            if obj in d:
                d.remove(obj)
        return set(d)
    
    def __iadd__(self, obj):
        if obj.__class__ == set:
            for item in obj:
                self.__d[item] = 1
        else:
            self.__d[obj] = 1
        return self
    
    def __isub__(self, obj):
        if obj.__class__ == set:
            for item in obj:
                if item in self:
                    del self.__d[item]
        else:
            if obj in self.__d:
                del self.__d[obj]
        return self
    
    def __len__(self):
        return len(self.__d)

    def __contains__(self, item):
        return item in self.__d

    def __repr__(self):
        return "set(%s)" % repr(self.__d.keys())

    def __iter__(self):
        return self.__d.__iter__()

#### DECAYING SET

import time

class DecayingSet:
    """
    A set where the members are removed over time.
    """

    def __init__(self, ttl):
        self.ttl = ttl
        self.set_1 = set()
        self.time_created_1 = time.time()
        self.set_2 = set()
        self.time_created_2 = time.time()
        self.current_set = 1

    def add(self, item):
        self.refresh()
        if self.current_set == 1:
            self.set_1 += item
        else:
            self.set_2 += item

    def refresh(self):
        if self.current_set == 1:
            if time.time() > self.time_created_1 + self.ttl:
                self.set_2 = set()
                self.time_created_2 = time.time()
                self.current_set = 2
        else:
            if time.time() > self.time_created_2 + self.ttl:
                self.set_1 = set()
                self.time_created_1 = time.time()
                self.current_set = 1

    def __contains__(self, item):
        return (item in self.set_1) or (item in self.set_2)

    def __len__(self):
        return len(self.set_1) + len(self.set_2)

    # @@@ only implemented methods that are currently in use

#### CORE CLASSES

class Node(asyncore.dispatcher):
    """
    A node in the P2P network.

    A Node listens on a particular address/port and can receive
    inward connections there. It can also make outward connections.
    All Nodes must have a unique identifier (uid).
    """
    
    def __init__(self, uid, addr):
        
        # listen on the given address
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(addr)
        self.listen(5)

        # unique identifier
        self.uid = uid

        # dictionary of set of connections keyed by uid
        # for a given uid, set contains all direct connections to that uid
        self.connections = {}

        # dictionary of set of remote nodes keyed by proxy uid
        # for a given proxy, set contains uids of all nodes proxy can contact 
        self.proxies = {}

        self.next_message_id = 1
        self.message_set = DecayingSet(60)

        print "node %s listening at %s" % (uid, repr(addr))


    ### asyncore.dispatcher methods

    def handle_accept(self):
        InwardConnection(self, self.accept())

    ### own methods

    def register(self, id, connection):
        """
        Register the given connection as being to a node with the given id.

        Note: the id might not be the uid of the node, it could be a group id.
        """

        # add the connection, creating the set if one does not exist
        s = self.connections.setdefault(id, set())
        s += connection

        # refresh connection knowledge with neighbours
        self.refresh()
        
        print "registered", id
        print "conections:", self.connections
        
    def deregister(self, id, connection):
        """
        Remove the given connection as being to a node with the given id.

        This could be because the connection has been lost or, in the case
        of a group id, that the remote node has left that group
        """

        # @@@ should a node be prohibited from deregistering its uid?

        # if there is no connection for that id...
        if not id in self.connections:
            return # @@@ should there be an error of some sort?

        # remove the connection
        self.connections[id] -= connection

        # if that was the last connection for that id...
        if len(self.connections.get(id, [])) == 0:
            # remove the set
            del self.connections[id]
            # and remove any knowledge of that node as a proxy
            if id in self.proxies:
                del self.proxies[id]
                
            print "deregistered", id

        print "conections:", self.connections
        print "proxies:", self.proxies

        # refresh connection knowledge with neighbours
        self.refresh()

    def deregister_all(self, connection):
        """
        Remove the given connection as being to a node with any id.

        This is generally because the connection has been lost.
        """
        
        for id in self.connections.keys():
            if connection in self.connections[id]:
                self.deregister(id, connection)
    
    def who(self, avoid=None):
        """
        Returns a list of the ids of nodes that this node knows how to contact.

        If an avoid argument is given, the node of that uid is neither included
        in the list nor considered as an available proxy. Usually avoid would
        be set to the uid of the remote node that is asking the question.
        """

        # @@@ could be rewritten to use sets
        
        list = []

        # direct connections
        for uid in self.connections:
            if avoid and uid != avoid:
                list.append(uid)

        # connections via proxy        
        for proxy in self.proxies:
            if avoid and proxy != avoid:
                for node in self.proxies[proxy]:
                    if not node in list:
                        list.append(node)

        return list

    def _add_proxy(self, proxy, node_list):
        self.proxies[proxy] = set(node_list)
        print "proxies:", self.proxies
        self.refresh()

    def can_proxy(self, proxy, node_list):
        """
        Informs this node that proxy can act as proxy for nodes in node_list.
        """

        # @@@ this can be simplified using sets
        if not proxy in self.proxies:
            self._add_proxy(proxy, node_list)
            return
        for item in self.proxies[proxy]:
            if not item in node_list:
                self._add_proxy(proxy, node_list)
                return
        for item in node_list:
            if not item in self.proxies[proxy]:
                self._add_proxy(proxy, node_list)
                return
        
    def get_message_id(self):
        """
        Generates and returns a unique message identifier.
        """
        
        message_id = "%s-%s" % (self.uid, self.next_message_id)
        self.next_message_id = self.next_message_id + 1
        return message_id
        
    # TODO: better name
    def _check(self, to, frm, message_id, message):
        # if message has already been sent, don't resend
        if message_id in self.message_set:
            return 1 # 1 otherwise a duplicate is considered a failure

        # remember that this message has been sent
        # @@@ should this only be done if result == 1?
        self.message_set.add(message_id)
        print "message set size", len(self.message_set)
        
        return 0
        

    def tell(self, to, frm, message_id, message):
        """
        Send the given message directly and/or indirectly.
        """
        
        result = 0

        if self._check(to, frm, message_id, message):
            return 1

        # send directly if possible
        if to in self.connections:
            for connection in self.connections[to]:
                connection.send_says(to, frm, message_id, message)
                result = 1

        # send via proxy if possible
        for proxy in self.proxies:
            if to in self.proxies[proxy]:
                if proxy in self.connections:
                    # the above should be true but let's just check
                    for connection in self.connections[proxy]:
                        connection.send_pass_on(to, frm, message_id, message)
                        # @@@ we don't really know if it got to destination
                        result = 1

        return result

    def call(self, host, port):
        """
        Make outward connection to a node on the given host on the give port.
        """
        
        OutwardConnection(self, host, port)

        # refresh connection knowledge with neighbours
        self.refresh()

    def refresh(self):
        """
        Refresh knowledge of connection and proxies with neighbours.
        """
        
        for node in self.connections.keys():
            for connection in self.connections[node]:
                connection.send_who()
                connection.send_connected()


class Connection(asynchat.async_chat):
    """
    Abstract base class for both inward and outward connections.
    """
    
    def __init__(self, server):
        self.set_terminator("\r\n")
        self.server = server
        self.buffer = ""
        self.state = 0
        self.remote_uid = None
        self.send_i_am()
        self.set_reuse_addr()

    ### asynchat.async_chat methods
    
    def collect_incoming_data(self, data):
        self.buffer = self.buffer + data
        
    def found_terminator(self):
        data = self.buffer
        self.buffer = ""
        self.process(data)
        
    def handle_close(self):
        print "closing"
        self.server.deregister_all(self)
        self.close()

    ### own methods

    def process(self, data):
        """
        Process a command.
        """

        # @@@ can clean up more
        
        if self.state == 0: # ANONYMOUS
            
            if data[:4] == "QUIT":
                self.close()
            elif data[:4] == "I_AM":
                remote_uid = self.remote_uid = data[5:]
                self.server.register(remote_uid, self)
                self.state = 1
            elif data[:5] == "ERROR":
                pass # @@@
            else:
                self.send_error("UNKNOWN_COMMAND '%s'" % data)
                
        elif self.state == 1: # NORMAL
            if data[:4] == "QUIT":
                self.server.deregister_all(self)
                self.close()
            elif data[:4] == "I_AM":
                self.send_error("ALREADY_IDENTIFIED")
            elif data[:5] == "ERROR":
                pass # @@@
            elif data[:3] == "WHO":
                self.send_connected()
            elif data[:7] == "REFRESH":
                if len(data) == 7:
                    self.server.refresh()
                else:
                    self.server.refresh(data[8:])
            elif data[:9] == "CONNECTED":
                self.server.can_proxy(self.remote_uid, data[10:].split())
            elif data[:4] == "CALL":
                args = data[5:].split()
                host = args[0]
                port = int(args[1])
                self.server.call(host, port) # @@@ doesn't catch errors
            elif data[:4] == "JOIN":
                group_id = data[5:]
                self.server.register(group_id, self)
            elif data[:5] == "LEAVE":
                group_id = data[6:]
                self.server.deregister(group_id, self)
            elif data[:4] == "TELL":
                args = data[5:].split()
                destination = args[0]
                message = " ".join(args[1:])
                message = decode(message)
                message_id = self.server.get_message_id()
                if not self.server.tell(destination, self.remote_uid,
                                        message_id, message):
                    self.send_error("COULDN'T SEND")
            elif data[:7] == "PASS_ON":
                args = data[8:].split(" ", 3)
                destination = args[0]
                source = args[1]
                message_id = args[2]
                message = args[3]
                message = decode(message)
                if not self.server.tell(destination, source,
                                        message_id, message):
                    self.send_error("COULDN'T SEND")
            elif data[:4] == "CHAT":
                self.chat_destination = data[5:]
                self.send_chat_started()
                self.state = 2
            else:
                self.send_error("UNKNOWN_COMMAND '%s'" % data)
                
        elif self.state == 2: # CHAT MODE
            if data == "END_CHAT":
                self.chat_destination = None
                self.send_chat_ended()
                self.state = 1
            else:
                message_id = self.server.get_message_id()
                if not self.server.tell(self.chat_destination, self.remote_uid,
                                        message_id, data):
                    self.send_error("COULDN'T SEND")

    ### send methods
    #
    # Nodes don't know whether they are connected to another node or an edge
    # so the three-way classification below is typical rather than
    # enforced.

    ## messages normally sent only to edges

    def send_chat_started(self):
        self.push("CHAT_STARTED\r\n")

    def send_chat_ended(self):
        self.push("CHAT_ENDED\r\n")

    def send_error(self, message):
        self.push("ERROR %s\r\n" % message)

    def send_says(self, to, frm, message_id, message):
        message = encode(message)
        self.push("SAYS %s %s %s %s\r\n" % (to, frm, message_id, message))

    ## messages sent to both edges and other nodes

    def send_connected(self):
        connected_list = self.server.who(avoid=self.remote_uid)
        self.push("CONNECTED %s\r\n" % " ".join(connected_list))

    def send_i_am(self):
        self.push("I_AM %s\r\n" % self.server.uid)

    ## messages normally sent only to other nodes
        
    def send_pass_on(self, to, frm, message_id, message):
        message = encode(message)
        self.push("PASS_ON %s %s %s %s\r\n" % (to, frm, message_id, message))

    def send_who(self):
        self.push("WHO\r\n")
            


class InwardConnection(Connection):
    """
    Created by a Node for each inward connection received.
    """
    
    def __init__(self, server, (conn, addr)):
        asynchat.async_chat.__init__(self, conn)
        Connection.__init__(self, server)
        print "connection from", addr


class OutwardConnection(Connection):
    """
    Created by a Node when instructed to make an outward call.
    """
    
    def __init__(self, server, host, port):
        asynchat.async_chat.__init__(self)
        self.set_terminator(None)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        Connection.__init__(self, server)
        self.connect((host, port))
        self.send_i_am()
        print "connection to", host, port


        
        
def encode(message):
    orig = message
    message = '\\\\'.join(message.split('\\'))
    message = '\\n'.join(message.split('\n'))
    if not decode(message)==orig:
        print "ORIG:", orig, "\n\nAFTER:", decode(message)
    return message


def decode(message):
    message = "\n".join(message.split("\\n"))
    return "\\".join(message.split("\\\\"))

#### MAINLINE

if __name__ == "__main__":
    if len(sys.argv) == 3:
        addr = ("", int(sys.argv[1]))
        n = Node(sys.argv[2], addr)
        asyncore.loop()
    else:
        print "usage: p2p.py <port> <uid>"
