ANY = None

class TripleStore(object):

    def __init__(self):
        # indexed by [subject][predicate][object]
        self.spo = {}

        # indexed by [predicate][object][subject]
        self.pos = {}

    def add(self, s, p, o):
        
        # spo
        spo = self.spo
        if not spo.has_key(s):
            spo[s] = {}

        subjectDictionary = spo[s]
        if not subjectDictionary.has_key(p):
            subjectDictionary[p] = {}

        subjectDictionary[p][o] = 1

        # pos
        pos = self.pos
        if not pos.has_key(p):
            pos[p] = {}

        predicateDictionary = pos[p]
        if not predicateDictionary.has_key(o):
            predicateDictionary[o] = {}

        predicateDictionary[o][s] = 1

    def __remove(self, subject, predicate, object):
        del self.spo[subject][predicate][object]
        del self.pos[predicate][object][subject]

    # TODO: remove should take a triple not three args
    def remove(self, subject=ANY, predicate=ANY, object=ANY):
        self.visit(self.__remove, (subject, predicate, object))

    def visit(self, callback, (subject, predicate, object)):
        if subject!=ANY: # subject is given
            spo = self.spo
            if spo.has_key(subject):
                subjectDictionary = spo[subject]
                if predicate!=ANY: # subject+predicate is given
                    if subjectDictionary.has_key(predicate):
                        if object!=ANY: # subject+predicate+object is given
                            if subjectDictionary[predicate].has_key(object):
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
                            if subjectDictionary[p].has_key(object):
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
            if pos.has_key(predicate):
                predicateDictionary = pos[predicate]
                if object!=ANY: # predicate+object is given, subject unbound
                    if predicateDictionary.has_key(object):
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
                if predicateDictionary.has_key(object):
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

    # TODO: this method might get refactored back into visit
    def visit_subjects(self, callback):
        """
        Experimental -- may change, depend on it at your own risk

        This method differs from visit(aSubject, ANY, ANY) in that it will only
        call the callback once per subject.
        """
        for s in self.spo.keys():
            callback(s, ANY, ANY)
