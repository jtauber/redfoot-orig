from threading import RLock
from threading import Condition

class ConnectionCubby:

    def __init__(self, limit):
        self.mon = RLock()
        self.rc = Condition(self.mon)
        self.wc = Condition(self.mon)
        self.limit = limit
        self.queue = []

    def put(self, item):
        self.mon.acquire()
        while len(self.queue) >= self.limit:
            self.wc.wait()
        self.queue.append(item)
        self.rc.notify()
        self.mon.release()

    def get(self):
        self.mon.acquire()
        if not self.queue:
            item = None
        else:
            item = self.queue[0]
            del self.queue[0]
            self.wc.notify()
        self.mon.release()
        return item

    def empty(self):
        if not self.queue:
            return 1
        else:
            return 0
        

    def wait(self, timeout=None):
        self.mon.acquire()
        self.rc.wait(timeout)
        self.mon.release()

    def notify(self):
        self.mon.acquire()
        self.rc.notify()
        self.mon.release()
