from threading import RLock
from threading import Condition

from redfoot.rdf.store.storeio import TripleStoreIO

class AutoSaveStoreIO(TripleStoreIO):
    def __init__(self):
        TripleStoreIO.__init__(self)
        self.dirtyBit = DirtyBit()
        
    def remove(self, subject=None, predicate=None, object=None):
        self.dirtyBit.set()
        TripleStoreIO.remove(self, subject, predicate, object)

    def add(self, subject, predicate, object):
        self.dirtyBit.set()
        TripleStoreIO.add(self, subject, predicate, object)

    def load(self, location, URI=None):
        TripleStoreIO.load(self, location, URI)
        self.dirtyBit.clear() # we just loaded... therefore we are clean
        self._start_thread() 

    def _start_thread(self, notMoreOftenThan=5*60):
        """Not more often then is in seconds"""
        import threading
        t = threading.Thread(target = self._autosave, args = (notMoreOftenThan,))
        t.setDaemon(1)
        t.start()
        
    def _autosave(self, interval):
        while 1:
            try:
                if self.dirtyBit.value()==1:
                    self.dirtyBit.clear()
                    import sys
                    sys.stderr.write("auto saving\n")
                    self.save(self.location, self.URI)
                    self.save("%s-%s" % (self.location, self.date_time_string()), self.URI)
                    # Do not save a backup more often than interval
                    import time
                    time.sleep(interval)
            except:
                import traceback
                traceback.print_exc()
                sys.stderr.flush()
            # do not bother to check if dirty until we get notified
            self.dirtyBit.wait()

    # TODO: move somewhere more general
    def date_time_string(self, t=None):
        """."""
        import time
        if t==None:
            t = time.time()

        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
        # http://www.w3.org/TR/NOTE-datetime
        # 1994-11-05T08:15:30-05:00 corresponds to November 5, 1994, 8:15:30 am, US Eastern Standard Time
        #s = "%0004d-%02d-%2dT%02d:%02d:%02dZ" % ( year, month, day, hh, mm, ss)
        s = "%0004d-%02d-%02dT%02d_%02d_%02dZ" % ( year, month, day, hh, mm, ss)        
        return s


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





