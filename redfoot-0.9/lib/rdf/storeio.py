# $Header$

from store import TripleStore

class StoreIO:

    def load(self, location, URI=None):
        self.location = location
        if URI==None:
            # default to location
            self.URI = self.location
        else:
            self.URI = URI

        from rdf.parser import parseRDF
        parseRDF(self.add, self.location, self.URI)

    def save(self):
        self.saveAs(self.location, self.URI)

    def saveAs(self, location, URI):
        stream = open(location, 'w')
        self.output(stream, URI)
        stream.close()
        
    def output(self, stream, URI=None, subject=None, predicate=None, object=None):
        if URI==None:
            URI = self.URI

        from rdf.serializer import Serializer
        serializer = Serializer()

        serializer.setStream(stream)
        serializer.setBase(URI)

        self.visit(lambda s, p, o, serializer=serializer: serializer.registerProperty(p), subject, predicate, object)

        serializer.start()
        self.visit(serializer.triple, subject, predicate, object)
        serializer.end()


class TripleStoreIO(StoreIO, TripleStore):
    def add(self, subject, predicate, object):
        TripleStore.add(self, subject, predicate, object)

    def remove(self, subject=None, predicate=None, object=None):
        TripleStore.remove(self, subject=None, predicate=None, object=None)
        
        
from threading import RLock
from threading import Condition

class AutoSaveStoreIO(TripleStoreIO):

    def remove(self, subject=None, predicate=None, object=None):
        self.dirty.set()
        TripleStoreIO.remove(self, subject, predicate, object)

    def add(self, subject, predicate, object):
        self.dirty.set()
        TripleStoreIO.add(self, subject, predicate, object)

    def load(self, location, URI=None):
        self.dirty = Dirty()
        TripleStoreIO.load(self, location, URI)
        self.dirty.clear() # we just loaded... therefore we are clean
        self.autosave() 

    def autosave(self, notMoreOftenThan=10):
        """Not more often then is in seconds"""
        import threading
        t = threading.Thread(target = self._autosave, args = (notMoreOftenThan,))
        t.setDaemon(1)
        t.start()
        
    def _autosave(self, interval=5*60):
        while 1:
            if self.dirty.value()==1:
                self.dirty.clear()
                self.saveAs(self.location, self.URI)
                self.saveAs("%s-%s" % (self.location, self.date_time_string()), self.URI)
                # Do not save a backup more often than interval
                import time
                time.sleep(interval)
            # do not bother to check if dirty until we get notified
            self.dirty.wait()
        
    def date_time_string(self, t=None):
        """."""
        import time
        if t==None:
            t = time.time()

        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
        # http://www.w3.org/TR/NOTE-datetime
        # 1994-11-05T08:15:30-05:00 corresponds to November 5, 1994, 8:15:30 am, US Eastern Standard Time
        #s = "%0004d-%02d-%2dT%02d:%02d:%02dZ" % ( year, month, day, hh, mm, ss)
        s = "%0004d-%02d-%2dT%02d_%02d_%02dZ" % ( year, month, day, hh, mm, ss)        
        return s


class Dirty:
    def __init__(self):
        self.mon = RLock()
        self.rc = Condition(self.mon)
        self.dirty = 0
        
    def clear(self):
        self.mon.acquire()
        self.dirty = 0
        #self.rc.notify() only interested in knowing why we are dirty
        self.mon.release()

    def set(self):
        self.mon.acquire()
        self.dirty = 1
        self.rc.notify()
        self.mon.release()

    def value(self):
        return self.dirty

    def wait(self):
        self.mon.acquire()
        self.rc.wait()
        self.mon.release()


#~ $Log$
#~ Revision 4.12  2000/12/04 22:00:57  eikeon
#~ got rid of all the getStore().getStore() stuff by using Multiple inheritance and mixin classes instead of all the classes being wrapper classes
#~
#~ Revision 4.11  2000/12/04 03:24:09  jtauber
#~ bugfix: output was ignoring query
#~
#~ Revision 4.10  2000/12/04 02:36:29  jtauber
#~ cleaned up code
#~
#~ Revision 4.9  2000/12/04 02:28:32  jtauber
#~ serializer now keeps track of subject start/end state; query store no longer needed for output
#~
#~ Revision 4.8  2000/12/04 01:31:07  eikeon
#~ changed property/value to predicate/object
#~
#~ Revision 4.7  2000/12/04 01:26:44  eikeon
#~ no more getStore() on StoreIO
#~
#~ Revision 4.6  2000/12/04 01:17:40  eikeon
#~ refactored output methods into one method that takes a query style set of subject, predicate, object to output
#~
#~ Revision 4.5  2000/12/04 01:00:58  eikeon
#~ Seperated out auto save stuff into AutoSaveStoreIO subclass
#~
#~ Revision 4.4  2000/12/03 22:27:07  jtauber
#~ updated to use new parseRDF function
#~
#~ Revision 4.3  2000/11/29 23:29:05  eikeon
#~ Added autosave functionailty
#~
#~ Revision 4.2  2000/11/21 03:16:46  eikeon
#~ rewrote slow inefficient output method
#~
#~ Revision 4.1  2000/11/20 21:31:58  jtauber
#~ added a method that outputs to a given stream the serialized results of a query
#~
#~ Revision 4.0  2000/11/06 15:57:33  eikeon
#~ VERSION 4.0
#~
#~ Revision 3.1  2000/11/02 21:48:27  eikeon
#~ removed old log messages
#~
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
