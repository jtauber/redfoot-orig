from threading import RLock
ANY = None

class TripleStore(object):

    def __init__(self):
        # indexed by [subject][predicate][object]
        self.spo = {}

        # indexed by [predicate][object][subject]
        self.pos = {}
        self.count = 0
        self.lock = RLock()
        self.pending_removes = []
        self.pending_adds = []

    def add(self, s, p, o):
        if self.count==0:
            # spo
            self.spo.setdefault(s, {}).setdefault(p, {})[o] = 1

            # pos
            self.pos.setdefault(p, {}).setdefault(o, {})[s] = 1
        else:
            self.pending_adds.append((s, p, o))

    def __remove(self, subject, predicate, object):
        if self.count==0:
            del self.spo[subject][predicate][object]
            del self.pos[predicate][object][subject]
        else:
            self.pending_removes.append((subject, predicate, object))

    def remove(self, subject=ANY, predicate=ANY, object=ANY):
        self.visit(self.__remove, (subject, predicate, object))

    def visit(self, callback, (subject, predicate, object)):
        self.lock.acquire()
        self.lock.release()                        
        self.count = self.count + 1
        pending_removes = self.pending_removes
        def cb(s, p, o):
            if not (s, p, o) in pending_removes:
                stop = callback(s, p, o)
                if stop:
                    return stop
        stop = self.__visit(cb, (subject, predicate, object))
        if stop:
            self.count = self.count - 1            
            return stop
        for (s, p, o) in self.pending_adds:
            if (subject==ANY or subject==s) and (predicate==ANY or predicate==p) and (object==ANY or object==o):
                stop = callback(s, p, o)
                if stop:
                    self.count = self.count - 1                    
                    return stop
        self.count = self.count - 1
        if self.count==0:
            self.lock.acquire()
            pending_removes = self.pending_removes
            while pending_removes:
                (s, p, o) = pending_removes.pop()
                self.__remove(s, p, o)
            pending_adds = self.pending_adds                
            while pending_adds:
                (s, p, o) = pending_adds.pop()
                self.add(s, p, o)
            self.lock.release()

    def __visit(self, callback, (subject, predicate, object)):        
        """
        Visit all the triples that match the given triple mask by
        calling callback. The triple mask is a triple where any or all
        of subject, predicate, object may be ANY (AKA None).
        """
        
        if subject!=ANY: # subject is given
            spo = self.spo
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
            pos = self.pos
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
            pos = self.pos
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
            spo = self.spo
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
        for s in self.spo.keys():
            callback(s, ANY, ANY)


