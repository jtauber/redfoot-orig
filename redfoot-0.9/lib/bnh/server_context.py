# $Header$
import time

class ServerContext:
    def __init__(self):
        self.sessions = {}
        self.cubby = Cubby()
        import threading
        t = threading.Thread(target = self._session_reaper, args = ())
        t.setDaemon(1)
        t.start()

    def _session_reaper(self):
        while 1:
            sessionKey = self.cubby.peek()
            if sessionKey==None:
                self.cubby.wait(1)
            else:
                import time
                now = time.time()
                session = self.sessions[sessionKey]
                
                idle = (now - session.getLastAccessedTime())
                if idle > session.getMaxInactiveInterval():
                    self.cubby.get() # todo... pop
                    del self.sessions[sessionKey]
                else:
                    delta = session.getMaxInactiveInterval() -  idle
                    self.cubby.wait(delta)

    def add_session(self, session):
        self.cubby.put(session)

    def get_session(self, key):
        sessions = self.sessions
        if sessions.has_key(key):
            return sessions[key]
        else:
            return None
        
    def create_session(self):
        from whrandom import random
        rn = random()
        key = "%s#T%s" % (rn, time.time())

        #if self.sessions.has_key(key):
        #    raise "TODO: exception"
        session = Session(key)
        self.sessions[key] = session
        self.cubby.put(key)

        return session

class Session:
    def __init__(self, id):
        now = time.time()
        self._creationTime = now
        self._setLastAccessedTime(now)
        self._attributes = {}
        self.maxInactiveInterval = 3600*24*365*10 # default ~10 years
        self._id = id

    def getAttribute(self, name):
        if self._attributes.has_key(name):
            return self._attributes[name]
        else:
            return None
    
    def getAttributeNames(self):
        return self._attributes.keys()
    
    def getCreationTime(self):
        return self._creationTime

    def getId(self):
        return self._id

    def getLastAccessedTime(self):
        return self._lastAccessedTime

    def _setLastAccessedTime(self, time):
        self._lastAccessedTime = time

    def getMaxInactiveInterval(self):
        return self.maxInactiveInterval

    def setMaxInactiveInterval(self, interval):
        self._maxInactiveInterval = interval

    def invalidate(self):
        self._invalid = 1

    def isNew(self):
        return self.new==1

    def removeAttribute(self, name):
        del self.attributes[name]

    def setAttribute(self, name, value):
        self.attributes[name] = value

    def setMaxInactiveInterval(self, interval):
        self._maxInactiveInterval = interval
    


from threading import RLock
from threading import Condition

class Cubby:

    def __init__(self):
        self.mon = RLock()
        self.rc = Condition(self.mon)
        self.wc = Condition(self.mon)
        self.queue = []

    def put(self, item):
        self.mon.acquire()
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

    def peek(self):
        self.mon.acquire()
        if not self.queue:
            item = None
        else:
            item = self.queue[0]
        self.mon.release()
        return item

    def wait(self, timeout=None):
        self.mon.acquire()
        self.rc.wait(timeout)
        self.mon.release()


#~ $Log$
#~ Revision 6.2  2001/03/26 20:19:01  eikeon
#~ removed old header
#~
#~ Revision 6.1  2001/03/13 04:02:50  eikeon
#~ fixed cookies so that they persist a very long time; changed default max inactive time to 10 years
#~
#~ Revision 6.0  2001/02/19 05:01:23  jtauber
#~ new release
