from threading import RLock

ANY = None


class TripleStore(object):
    """\
An in memory implementation of a triple store.

This triple store uses nested dictionaries to store triples. Each
triple is stored in two such indices as follows spo[s][p][o] = 1 and
pos[p][o][s] = 1.

This implementation also makes use of lists for pending adds and
removes so that the dictionaries can be iterated over directly while
visiting.
    """    
    def __init__(self):
        # indexed by [subject][predicate][object]
        self.__spo = {}

        # indexed by [predicate][object][subject]
        self.__pos = {}

        # number of calls to visit still in progress
        self.__visit_count = 0

        # lock for locking down the indices
        self.__lock = RLock()

        # lists for keeping track of added and removed triples while
        # we wait for the lock
        self.__pending_removes = []
        self.__pending_adds = []

    def add(self, s, p, o):
        """\
Add a triple to the store of triples.
        """
        if self.__visit_count==0:
            # If not visiting add triple to indices by adding
            # dictionary entries for spo[s][p][p] = 1 and pos[p][o][s]
            # = 1 creating the nested dictionaries where they do not
            # yet exits.
            self.__spo.setdefault(s, {}).setdefault(p, {})[o] = 1
            self.__pos.setdefault(p, {}).setdefault(o, {})[s] = 1
        else:
            self.__pending_adds.append((s, p, o))

    def __remove(self, subject, predicate, object):
        # TODO: split this into two methods having caller check which
        # to call
        if self.__visit_count==0:
            # If not visiting remove triples from the indices.
            del self.__spo[subject][predicate][object]
            del self.__pos[predicate][object][subject]
        else:
            self.__pending_removes.append((subject, predicate, object))

    def remove(self, subject=ANY, predicate=ANY, object=ANY):
        self.visit(self.__remove, (subject, predicate, object))

    def visit(self, callback, (subject, predicate, object)):
        lock = self.__lock
        pending_removes = self.__pending_removes
        if pending_removes:
            def callback_pending_removes(s, p, o):
                """Only calls callback if triple is not in pending_removes."""
                if not (s, p, o) in pending_removes:
                    stop = callback(s, p, o)
                    if stop:
                        return stop
            cb = callback_pending_removes
        else:
            cb = callback

        self.__visit_count = self.__visit_count + 1
        # Acquire lock for indices so that they will not change while
        # we iterate over them
        lock.acquire()
        try:
            stop = self.__visit(cb, (subject, predicate, object))
        finally:
            lock.release()        
            self.__visit_count = self.__visit_count - 1                    

        if stop:
            return stop
        for (s, p, o) in self.__pending_adds:
            if (subject==ANY or subject==s) and (predicate==ANY or predicate==p) and (object==ANY or object==o):
                stop = callback(s, p, o)
                if stop:
                    return stop

        if self.__visit_count==0:
            # Acquire lock for indices while we update them.
            lock.acquire()
            pending_removes = self.__pending_removes
            while pending_removes:
                (s, p, o) = pending_removes.pop()
                self.__remove(s, p, o)
            pending_adds = self.__pending_adds                
            while pending_adds:
                (s, p, o) = pending_adds.pop()
                self.add(s, p, o)
            lock.release()

    def __visit(self, callback, (subject, predicate, object)):        
        """
        Visit all the triples that match the given triple mask by
        calling callback. The triple mask is a triple where any or all
        of subject, predicate, object may be ANY (AKA None).
        """
        
        if subject!=ANY: # subject is given
            spo = self.__spo
            if subject in spo:
                subjectDictionary = spo[subject]
                if predicate!=ANY: # subject+predicate is given
                    if predicate in subjectDictionary:
                        if object!=ANY: # subject+predicate+object is given
                            if object in subjectDictionary[predicate]:
                                stop = callback(subject, predicate, object)
                                if stop:
                                    return stop
                            else: # given object not found
                                pass
                        else: # subject+predicate is given, object unbound
                            for o in subjectDictionary[predicate]:
                                stop = callback(subject, predicate, o)
                                if stop:
                                    return stop
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in subjectDictionary:
                        if object!=ANY: # object is given
                            if object in subjectDictionary[p]:
                                stop = callback(subject, p, object)
                                if stop:
                                    return stop
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in subjectDictionary[p]:
                                stop = callback(subject, p, o)
                                if stop:
                                    return stop
            else: # given subject not found
                pass
        elif predicate!=ANY: # predicate is given, subject unbound
            pos = self.__pos
            if predicate in pos:
                predicateDictionary = pos[predicate]
                if object!=ANY: # predicate+object is given, subject unbound
                    if object in predicateDictionary:
                        for s in predicateDictionary[object]:
                            stop = callback(s, predicate, object)
                            if stop:
                                return stop
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in predicateDictionary:
                        for s in predicateDictionary[o]:
                            stop = callback(s, predicate, o)
                            if stop:
                                return stop
        elif object!=ANY: # object is given, subject+predicate unbound
            pos = self.__pos
            for p in pos:
                predicateDictionary = pos[p]
                if object in predicateDictionary:
                    for s in predicateDictionary[object]:
                        stop = callback(s, p, object)
                        if stop:
                            return stop
                else: # given object not found
                    pass
        else: # subject+predicate+object unbound
            spo = self.__spo
            for s in spo:
                subjectDictionary = spo[s]
                for p in subjectDictionary:
                    for o in subjectDictionary[p]:
                        stop = callback(s, p, o)
                        if stop:
                            return stop

    # Alternative triple store implementations need not implement this
    # method as it can be implemented on top of the others. Although
    # it will likely be more efficient to implement at the triple
    # store level. 
    def visit_subjects(self, callback):
        """
        Experimental -- may change, depend on it at your own risk

        This method differs from visit(aSubject, ANY, ANY) in that it will only
        call the callback once per subject.
        """
        for s in self.__spo.keys():
            callback(s, ANY, ANY)


