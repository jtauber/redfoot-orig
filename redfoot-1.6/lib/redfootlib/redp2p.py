from redfootlib.p2p import Node

class CacheNode(Node, object):
    def __init__(self, uid, addr):
        super(CacheNode, self).__init__(uid, addr)
        self.message_set = []
        self.last_message = {}

    def _check(self, to, frm, message_id, message):
        msg = (to, frm, message_id, message)
        if msg in self.message_set:  # don't resend
            return 1 # 1 otherwise a duplicate is considered a failure
        self.message_set.append(msg)
        print "message set size", len(self.message_set)
        return 0

    def _add_proxy(self, proxy, node_list):
        super(CacheNode, self)._add_proxy(proxy, node_list)
        for connection in self.connections[proxy]:
            self._backlog(connection, 0)

    def register(self, id, connection):
        super(CacheNode, self).register(id, connection)
        self._backlog(connection, 0)
        
    def _backlog(self, connection, tell=1):
        message_set = self.message_set
        msg = self.last_message.setdefault(connection.remote_uid, None)        
        if msg:
            start = message_set.index(msg) + 1
        else:
            start = 0
        for i in xrange(start, len(message_set)):
            msg = to, frm, message_id, message = message_set[i]
            print to, connection.remote_uid, getattr(connection, 'uid', None)
            if to==connection.remote_uid:
                connection.send_says(to, frm, message_id, message)
            else:
                connection.send_pass_on(to, frm, message_id, message)
        self.last_message[connection.remote_uid] = msg
