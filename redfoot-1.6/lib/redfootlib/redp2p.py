from redfootlib.p2p import Node

class CacheNode(Node, object):
    def __init__(self, uid, addr):
        super(CacheNode, self).__init__(uid, addr)
        self.message_set = []
        self.last_message = {}

    def _check(self, to, frm, message_id, message):
        msg = (to, frm, message_id, message)
        # if message has already been sent, don't resend
        if msg in self.message_set:
            return 1 # 1 otherwise a duplicate is considered a failure

        self.message_set.append(msg)
        
        print "message set size", len(self.message_set)
        return 0

    def _add_proxy(self, proxy, node_list):
        super(CacheNode, self)._add_proxy(proxy, node_list)

        message_set = self.message_set
        for connection in self.connections[proxy]:
            last_message = self.last_message.setdefault(connection.remote_uid, None)
            if last_message:
                start = message_set.index(last_message) + 1
            else:
                start = 0
            for i in xrange(start, len(message_set)):
                msg = message_set[i]
                self._send_pass_on(connection, msg)

    def _send_pass_on(self, connection, msg):
        super(CacheNode, self)._send_pass_on(connection, msg)
        self.last_message[connection.remote_uid] = msg
