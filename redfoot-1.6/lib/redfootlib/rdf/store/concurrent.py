from __future__ import generators

from threading import Lock

class ResponsibleGenerator(object):
    """A generator that will help clean up when it is done being used."""

    # TODO: add explicit calling of cleanup? Or should we rely on
    # __del__ to get called
    
    __slots__ = ['cleanup', 'gen']

    def __init__(self, gen, cleanup):
        self.cleanup = cleanup
        self.gen = gen
 
    def __del__(self):
        self.cleanup()
 
    def __iter__(self):
        return self
 
    def next(self):
        return self.gen.next()


class Concurrent(object):

    def __init__(self):
        super(Concurrent, self).__init__()
        
        # number of calls to visit still in progress
        self.__visit_count = 0

        # lock for locking down the indices
        self.__lock = Lock()

        # lists for keeping track of added and removed triples while
        # we wait for the lock
        self.__pending_removes = []
        self.__pending_adds = []

    def add(self, s, p, o):
        if self.__visit_count==0:
            super(Concurrent, self).add(s, p, o)
        else:
            self.__pending_adds.append((s, p, o))

    def remove(self, subject, predicate, object):
        if self.__visit_count==0:
            super(Concurrent, self).remove(s, p, o)            
        else:
            self.__pending_removes.append((subject, predicate, object))

    def triples(self, subject, predicate, object):
        g = super(Concurrent, self).triples(subject, predicate, object)
        pending_removes = self.__pending_removes
        self.__begin_read()
        for s, p, o in ResponsibleGenerator(g, self.__end_read):
            if not (s, p, o) in pending_removes:
                yield s, p, o

        for (s, p, o) in self.__pending_adds:
            if (subject==None or subject==s) and (predicate==None or predicate==p) and (object==None or object==o):
                yield s, p, o

    def __begin_read(self):
        lock = self.__lock 
        lock.acquire()                
        self.__visit_count = self.__visit_count + 1
        lock.release()

    def __end_read(self):
        lock = self.__lock                
        lock.acquire()                        
        self.__visit_count = self.__visit_count - 1
        if self.__visit_count==0:
            pending_removes = self.__pending_removes
            while pending_removes:
                (s, p, o) = pending_removes.pop()
                self.remove(s, p, o)
            pending_adds = self.__pending_adds                
            while pending_adds:
                (s, p, o) = pending_adds.pop()
                self.add(s, p, o)
        lock.release()                        


    
