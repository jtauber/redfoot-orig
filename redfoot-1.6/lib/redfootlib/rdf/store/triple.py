ANY = None

class TripleStore(object):

    def __init__(self):
        # indexed by [subject][predicate][object]
        self.spo = {}

        # indexed by [predicate][object][subject]
        self.pos = {}

    def add(self, s, p, o):
        
        # spo
        self.spo.setdefault(s, {}).setdefault(p, {})[o] = 1

        # pos
        self.pos.setdefault(p, {}).setdefault(o, {})[s] = 1

    def __remove(self, subject, predicate, object):
        del self.spo[subject][predicate][object]
        del self.pos[predicate][object][subject]

    def remove(self, subject=ANY, predicate=ANY, object=ANY):
        self.visit(self.__remove, (subject, predicate, object))

    def visit(self, callback, (subject, predicate, object)):
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
                            for o in subjectDictionary[predicate].keys():
                                stop = callback(subject, predicate, o)
                                if stop:
                                    return stop
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in subjectDictionary.keys():
                        if object!=ANY: # object is given
                            if object in subjectDictionary[p]:
                                stop = callback(subject, p, object)
                                if stop:
                                    return stop
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in subjectDictionary[p].keys():
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
                        for s in predicateDictionary[object].keys():
                            stop = callback(s, predicate, object)
                            if stop:
                                return stop
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in predicateDictionary.keys():
                        for s in predicateDictionary[o].keys():
                            stop = callback(s, predicate, o)
                            if stop:
                                return stop
        elif object!=ANY: # object is given, subject+predicate unbound
            pos = self.pos
            for p in pos.keys():
                predicateDictionary = pos[p]
                if object in predicateDictionary:
                    for s in predicateDictionary[object].keys():
                        stop = callback(s, p, object)
                        if stop:
                            return stop
                else: # given object not found
                    pass
        else: # subject+predicate+object unbound
            spo = self.spo
            for s in spo.keys():
                subjectDictionary = spo[s]
                for p in subjectDictionary.keys():
                    for o in subjectDictionary[p].keys():
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


