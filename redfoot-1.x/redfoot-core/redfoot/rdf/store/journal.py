from redfoot.rdf.const import *

from redfoot.rdf.literal import literal, un_literal, is_literal

ADD = literal("add")
DELETE = literal("delete")
OPERATION = "http://redfoot.sourceforge.net/2001/01/30/#operation"
TIMESTAMP = "http://redfoot.sourceforge.net/2001/01/30/#timestamp"
SOURCE = "http://redfoot.sourceforge.net/2001/01/30/#source"

#from redfoot.rdf.query import QueryStore
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


class JournalingStoreIO(StoreIO, JournalingStore):

    def __init__(self):
        StoreIO.__init__(self)
        JournalingStore.__init__(self)
        from redfoot.redfoot.rednode import Local
        #self.journal = Local()

    def load(self, location, URI=None):
        from redfoot.redfoot.rednode import Local
        journal = Local()
        journal.location = "%s-J.rdf" % location[:-4]
        journal.URI = URI
        journal.dirtyBit.clear() # we just loaded... therefore we are clean
        journal._start_thread()
        self.journal = journal
        StoreIO.load(self, location, URI)

    def load_journal(self, location, URI=None):
        from redfoot.redfoot.rednode import Local
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











