from __future__ import generators

ANY = None


class InMemoryStore(object):
    """\
An in memory implementation of a triple store.

This triple store uses nested dictionaries to store triples. Each
triple is stored in two such indices as follows spo[s][p][o] = 1 and
pos[p][o][s] = 1.
    """    
    def __init__(self):
        super(InMemoryStore, self).__init__()
        
        # indexed by [subject][predicate][object]
        self.__spo = {}

        # indexed by [predicate][object][subject]
        self.__pos = {}

    def add(self, s, p, o):
        """\
        Add a triple to the store of triples.
        """
        # add dictionary entries for spo[s][p][p] = 1 and pos[p][o][s]
        # = 1, creating the nested dictionaries where they do not yet
        # exits.
        self.__spo.setdefault(s, {}).setdefault(p, {})[o] = 1
        self.__pos.setdefault(p, {}).setdefault(o, {})[s] = 1

    def remove(self, subject, predicate, object):
        del self.__spo[subject][predicate][object]
        del self.__pos[predicate][object][subject]

    def triples(self, subject, predicate, object):
        """A generator over all the triples matching """
        if subject!=ANY: # subject is given
            spo = self.__spo
            if subject in spo:
                subjectDictionary = spo[subject]
                if predicate!=ANY: # subject+predicate is given
                    if predicate in subjectDictionary:
                        if object!=ANY: # subject+predicate+object is given
                            if object in subjectDictionary[predicate]:
                                yield subject, predicate, object
                            else: # given object not found
                                pass
                        else: # subject+predicate is given, object unbound
                            for o in subjectDictionary[predicate].keys():
                                yield subject, predicate, o
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in subjectDictionary.keys():
                        if object!=ANY: # object is given
                            if object in subjectDictionary[p]:
                                yield subject, p, object
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in subjectDictionary[p].keys():
                                yield subject, p, o
            else: # given subject not found
                pass
        elif predicate!=ANY: # predicate is given, subject unbound
            pos = self.__pos
            if predicate in pos:
                predicateDictionary = pos[predicate]
                if object!=ANY: # predicate+object is given, subject unbound
                    if object in predicateDictionary:
                        for s in predicateDictionary[object].keys():
                            yield s, predicate, object
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in predicateDictionary.keys():
                        for s in predicateDictionary[o].keys():
                            yield s, predicate, o
        elif object!=ANY: # object is given, subject+predicate unbound
            pos = self.__pos
            for p in pos.keys():
                predicateDictionary = pos[p]
                if object in predicateDictionary:
                    for s in predicateDictionary[object].keys():
                        yield s, p, object
                else: # given object not found
                    pass
        else: # subject+predicate+object unbound
            spo = self.__spo
            for s in spo.keys():
                subjectDictionary = spo[s]
                for p in subjectDictionary.keys():
                    for o in subjectDictionary[p].keys():
                        yield s, p, o
                        
    def subjects(self):
        for s in self.__spo.keys():
            yield s

    def __iter__(self):
        return self.triples(ANY, ANY, ANY)
 


