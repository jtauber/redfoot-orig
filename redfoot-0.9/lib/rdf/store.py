# $Header$

class TripleStore:

    def __init__(self):
	# indexed by [subject][predicate][object]
        self.spo = {}

        # indexed by [predicate][object][subject]
        self.pos = {}

    def add(self, subject, predicate, object):
        # spo
        spo = self.spo
        if not spo.has_key(subject):
            spo[subject] = {}

        subjectDictionary = spo[subject]
        if not subjectDictionary.has_key(predicate):
            subjectDictionary[predicate] = {}

        subjectDictionary[predicate][object] = 1

        # pos
        pos = self.pos
        if not pos.has_key(predicate):
            pos[predicate] = {}

        predicateDictionary = pos[predicate]
        if not predicateDictionary.has_key(object):
            predicateDictionary[object] = {}

        predicateDictionary[object][subject] = 1

    def remove(self, subject=None, predicate=None, object=None):
        
        def callback(subject, predicate, object, spo=self.spo, pos=self.pos):
            del spo[subject][predicate][object]
            del pos[predicate][object][subject]

        self.visit(callback, subject, predicate, object)

    def visit(self, callback, subject=None, predicate=None, object=None):
        if subject!=None: # subject is given
            spo = self.spo
            if spo.has_key(subject):
                subjectDictionary = spo[subject]
                if predicate!=None: # subject+predicate is given
                    if subjectDictionary.has_key(predicate):
                        if object!=None: # subject+predicate+object is given
                            if subjectDictionary[predicate].has_key(object):
                                if callback(subject, predicate, object)!=None:
                                    return
                            else: # given object not found
                                pass
                        else: # subject+predicate is given, object unbound
                            for o in subjectDictionary[predicate].keys():
                                if callback(subject, predicate, o)!=None:
                                    return
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in subjectDictionary.keys():
                        if object!=None: # object is given
                            if subjectDictionary[p].has_key(object):
                                if callback(subject, p, object)!=None:
                                    return
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in subjectDictionary[p].keys():
                                if callback(subject, p, o)!=None:
                                    return
            else: # given subject not found
                pass
        elif predicate!=None: # predicate is given, subject unbound
            pos = self.pos
            if pos.has_key(predicate):
                predicateDictionary = pos[predicate]
                if object!=None: # predicate+object is given, subject unbound
                    if predicateDictionary.has_key(object):
                        for s in predicateDictionary[object].keys():
                            if callback(s, predicate, object)!=None:
                                return
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in predicateDictionary.keys():
                        for s in predicateDictionary[o].keys():
                            if callback(s, predicate, o)!=None:
                                return
        elif object!=None: # object is given, subject+predicate unbound
            pos = self.pos
            for p in pos.keys():
                predicateDictionary = pos[p]
                if predicateDictionary.has_key(object):
                    for s in predicateDictionary[object].keys():
                        if callback(s, p, object)!=None:
                            return
                else: # given object not found
                    pass
        else: # subject+predicate+object unbound
            spo = self.spo
            for s in spo.keys():
                subjectDictionary = spo[s]
                for p in subjectDictionary.keys():
                    for o in subjectDictionary[p].keys():
                        if callback(s, p, o)!=None:
                            return

    # TODO: this method might get refactored back into visit
    def visitSubjects(self, callback):
        """
        Experimental -- may change, depend on it at your own risk

        This method differs from visit(aSubject, None, None) in that it will only
        call the callback once per subject.
        """
        for s in self.spo.keys():
            callback(s)
                    

#~ $Log$
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
#~
#~ Revision 4.8  2000/12/06 19:40:30  eikeon
#~ moved get method to query as it can be layered on top of a TripleStore like all the other queries
#~
#~ Revision 4.7  2000/12/05 22:14:12  jtauber
#~ changed visitor class to function
#~
#~ Revision 4.6  2000/12/04 22:56:55  eikeon
#~ visit will now stop if None is not returned
#~
#~ Revision 4.5  2000/12/03 22:25:14  jtauber
#~ moved literal stuff to literal.py
#~
#~ Revision 4.4  2000/12/03 22:00:03  jtauber
#~ put literal handling code in store.py
#~
#~ Revision 4.3  2000/12/03 21:21:49  jtauber
#~ removed put; refactored remove to use callback function
#~
#~ Revision 4.2  2000/12/03 20:49:38  jtauber
#~ refactored+documented visit function
#~
#~ Revision 4.1  2000/12/03 20:17:40  jtauber
#~ changed property/value to predicate/object
#~
#~ Revision 4.0  2000/11/06 15:57:33  eikeon
#~ VERSION 4.0
#~
#~ Revision 3.1  2000/11/02 21:48:27  eikeon
#~ removed old log messages
#~
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
