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

    def _remove(self, subject, predicate, object):
        del self.spo[subject][predicate][object]
        del self.pos[predicate][object][subject]

    def remove(self, subject=None, predicate=None, object=None):
        self.visit(self._remove, subject, predicate, object)

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
    def visit_subjects(self, callback):
        """
        Experimental -- may change, depend on it at your own risk

        This method differs from visit(aSubject, None, None) in that it will only
        call the callback once per subject.
        """
        for s in self.spo.keys():
            callback(s)
                    


from rdf.const import *

from rdf.literal import literal
import time

ADD = literal("add")
DELETE = literal("delete")
OPERATION = "http://redfoot.sourceforge.net/2001/01/30/#operation"
TIMESTAMP = "http://redfoot.sourceforge.net/2001/01/30/#timestamp"

class JournalingStore(TripleStore):

    def __init__(self, journal):
        TripleStore.__init__(self)
        self.journal = journal
        self.sn = 0
        
    def generateURI(self):
        self.sn = self.sn + 1
        return "%s#T%s-%s" % (self.URI, time.time(), self.sn)

    def add(self, subject, predicate, object):
        TripleStore.add(self, subject, predicate, object)

        statement_uri = self.generateURI()
        self.journal.add(statement_uri, TYPE, STATEMENT)
        self.journal.add(statement_uri, SUBJECT, subject)
        self.journal.add(statement_uri, PREDICATE, predicate)
        self.journal.add(statement_uri, OBJECT, object)
        self.journal.add(statement_uri, OPERATION, ADD)

        self.journal.add(statement_uri, TIMESTAMP, date_time_filename())        
        
    def _remove(self, subject, predicate, object):
        TripleStore._remove(self, subject, predicate, object)

        statement_uri = self.generateURI()
        self.journal.add(statement_uri, TYPE, STATEMENT)
        self.journal.add(statement_uri, SUBJECT, subject)
        self.journal.add(statement_uri, PREDICATE, predicate)
        self.journal.add(statement_uri, OBJECT, object)
        self.journal.add(statement_uri, OPERATION, DELETE)

        self.journal.add(statement_uri, TIMESTAMP, date_time_filename())        

def date_time_filename(t=None):
    """."""
    import time
    if t==None:
        t = time.time()

    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
    s = "%0004d-%02d-%02dT%02d_%02d_%02dZ" % ( year, month, day, hh, mm, ss)        
    return s

#~ $Log$
#~ Revision 5.3  2000/12/17 20:56:09  eikeon
#~ renamed visitSubjects to visit_subjects
#~
#~ Revision 5.2  2000/12/17 20:41:22  eikeon
#~ removed log message prior to currently worked on release
#~
#~ Revision 5.1  2000/12/11 06:30:14  eikeon
#~ made some reasonably straight forward optimizations
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
