# $Header$
import time

class SN:
    def __init__(self):
        self.sn = 0
        self.time_path = None

    def get_sn(self):
        self.sn = self.sn + 1
        return self.sn

    def date_time_path(self, t=None):
        """."""
        
        if t==None:
            t = time.time()

        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)           
        time_path = "%0004d/%02d/%02d/T%02d/%02d/%02dZ" % ( year, month, day, hh, mm, ss)

        if time_path==self.time_path:
            sn = self.sn
            self.sn = sn + 1
        else:
            self.sn = 0
            self.time_path = time_path


        s = self.time_path + "%.004d" % self.sn
        return s

    
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

from rdf.literal import literal, un_literal, is_literal

ADD = literal("add")
DELETE = literal("delete")
OPERATION = "http://redfoot.sourceforge.net/2001/01/30/#operation"
TIMESTAMP = "http://redfoot.sourceforge.net/2001/01/30/#timestamp"
SOURCE = "http://redfoot.sourceforge.net/2001/01/30/#source"

#from rdf.query import QueryStore
#class JournalingStore(TripleStore, QueryStore):
class JournalingStore:

    def __init__(self):
        self.store = TripleStore()
        self.sn = SN()


    def chron(self, a, b):
        date_a = self.journal.getFirst(a[0], TIMESTAMP, None)
        if date_a!=None:
            date_a = un_literal(date_a[2])
        else:
            date_a = ''

        date_b = self.journal.getFirst(b[0], TIMESTAMP, None)
        if date_b!=None:
            date_b = un_literal(date_b[2])
        else:
            date_b = ''

        return cmp(date_a, date_b)

    def set_journal(self, journal):
        self.store.remove(None, None, None)
        self.journal = journal
        statements = self.journal.get(None, TYPE, STATEMENT)
        statements.sort(self.chron)
        for statement in statements:
            subject = statement[0]
            #print "s: %s -- ts: %s" % (subject, self.journal.getFirst(subject, TIMESTAMP, None)[2])
            s = self.journal.getFirst(subject, SUBJECT, None)
            p = self.journal.getFirst(subject, PREDICATE, None)
            o = self.journal.getFirst(subject, OBJECT, None)
            if s!=None and p!=None and o!=None:
                s = s[2]
                p = p[2]
                o = o[2]
            else:
                print (s, p, o)
                 
            operation = self.journal.getFirst(subject, OPERATION, None)
            if operation!=None:
                operation = operation[2]
            if operation==ADD:
                self.store.add(s, p, o)
            elif operation==DELETE:
                self.store.remove(s, p, o)

        
    def generateURI(self):
        return self.URI + self.sn.date_time_path()

    def add(self, subject, predicate, object):
        self.store.add(subject, predicate, object)

        statement_uri = self.generateURI()
        self.journal.add(statement_uri, TYPE, STATEMENT)
        self.journal.add(statement_uri, SUBJECT, subject)
        self.journal.add(statement_uri, PREDICATE, predicate)
        self.journal.add(statement_uri, OBJECT, object)
        self.journal.add(statement_uri, OPERATION, ADD)
        self.journal.add(statement_uri, SOURCE, self.URI)
        self.journal.add(statement_uri, TIMESTAMP, literal(self.sn.date_time_path()))
        
    def _remove(self, subject, predicate, object):
        self.store.remove(subject, predicate, object)

        statement_uri = self.generateURI()
        self.journal.add(statement_uri, TYPE, STATEMENT)
        self.journal.add(statement_uri, SUBJECT, subject)
        self.journal.add(statement_uri, PREDICATE, predicate)
        self.journal.add(statement_uri, OBJECT, object)
        self.journal.add(statement_uri, OPERATION, DELETE)
        self.journal.add(statement_uri, SOURCE, self.URI)
        self.journal.add(statement_uri, TIMESTAMP, literal(self.sn.date_time_path()))

    def remove(self, subject=None, predicate=None, object=None):
        self.visit(self._remove, subject, predicate, object)

    def visit(self, callback, subject=None, predicate=None, object=None):
        return self.store.visit(callback, subject, predicate, object)

    def visit_subjects(self, callback):
        self.store.visit_subjects(callback)

        
#~ $Log$
#~ Revision 7.0  2001/03/26 23:41:04  eikeon
#~ NEW RELEASE
