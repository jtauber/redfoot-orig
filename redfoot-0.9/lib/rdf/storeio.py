# $Header$

from store import TripleStore

# the following class can't be used by itself, it must be inherited by
# or along with a class that implements add(s,p,o) and
# visit(callback,s,p,o) 
class StoreIO:
    
    def __init__(self):
        self.URI = None
        
    def load(self, location, URI=None):
        self.location = location
        if URI==None:
            # default to location
            self.URI = self.location
        else:
            self.URI = URI

        from rdf.parser import parse_RDF
        parse_RDF(self.add, self.location, self.URI)

    def save(self, location=None, URI=None):
        if location==None:
            location = self.location
        if URI==None:
            URI = self.URI
        stream = open(location, 'w')
        self.output(stream, URI)
        stream.close()
        
    def input(self, stream, URI=None):
        from rdf.parser import parse_RDF_stream
        parse_RDF_stream(self.add, stream, URI)

    # TODO: maybe move this method 'down' a bit... as a URI is not
    # required to perform *a* serialization of a TripleStore?
    # Also, this method does not require a location.
    #   StoreIO->PersistantStore?
    def output(self, stream, URI=None, subject=None, predicate=None, object=None, absolute=0):
        if URI==None:
            URI = self.URI

        from rdf.serializer import Serializer
        serializer = Serializer()

        serializer.set_stream(stream)
        if absolute!=1:
            serializer.set_base_URI(URI)

        self.visit(lambda s, p, o, register_property=serializer.register_property: register_property(p), subject, predicate, object)

        serializer.start()
        self.visit(serializer.triple, subject, predicate, object)
        serializer.end()


class TripleStoreIO(StoreIO, TripleStore):
    def __init__(self):
        TripleStore.__init__(self)


from threading import RLock
from threading import Condition

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
            if self.dirtyBit.value()==1:
                self.dirtyBit.clear()
                # TODO: catch exceptions
                self.save(self.location, self.URI)
                self.save("%s-%s" % (self.location, self.date_time_string()), self.URI)
                # Do not save a backup more often than interval
                import time
                time.sleep(interval)
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


from rdf.store import *
class JournalingStoreIO(StoreIO, JournalingStore):

    def __init__(self):
        StoreIO.__init__(self)
        JournalingStore.__init__(self)
        from redfoot.rednode import Local
        #self.journal = Local()

    def load(self, location, URI=None):
        from redfoot.rednode import Local
        journal = Local()
        journal.location = "%s-J.rdf" % location[:-4]
        journal.URI = URI
        journal.dirtyBit.clear() # we just loaded... therefore we are clean
        journal._start_thread()
        self.journal = journal
        StoreIO.load(self, location, URI)

    def load_journal(self, location, URI=None):
        journal = Local()
        journal.load(location, URI)
        journal.dirtyBit.clear() # we just loaded... therefore we are clean
        journal._start_thread()
        self.location = "%s.rdf" % location[:-6]
        self.URI = URI
        self.set_journal(journal)

    def update_journal(self, stream, URI):
        self.journal.input(stream, URI)
        self.set_journal(self.journal)

    def save(self, location=None, URI=None):
        self.journal.save(location, URI)
        StoreIO.save(self, location, URI)


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


#~ $Log$
#~ Revision 6.1  2001/02/26 22:32:00  eikeon
#~ a bit more work on the journaling store stuff
#~
#~ Revision 6.0  2001/02/19 05:01:23  jtauber
#~ new release
#~
#~ Revision 5.6  2001/02/09 21:50:46  eikeon
#~ Added JournalingStoreIO and an input method
#~
#~ Revision 5.5  2000/12/20 20:37:17  eikeon
#~ changed mixed case to _ style... all except for query
#~
#~ Revision 5.4  2000/12/19 05:48:00  eikeon
#~ URI defaults to None so that output may be called without one; calling of __init__'s cleaned up
#~
#~ Revision 5.3  2000/12/17 21:12:46  eikeon
#~ fixed typo
#~
#~ Revision 5.2  2000/12/17 21:11:11  eikeon
#~ changed a couple mixed case names to _ style names
#~
#~ Revision 5.1  2000/12/17 20:41:22  eikeon
#~ removed log message prior to currently worked on release
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
