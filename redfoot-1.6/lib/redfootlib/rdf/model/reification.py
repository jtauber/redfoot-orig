from redfootlib.rdf.const import TYPE, STATEMENT
from redfootlib.rdf.const import SUBJECT, PREDICATE, OBJECT


class ReificationStore(object):
    """Mixin to enable reification."""
    
    def __init__(self):
        super(ReificationStore, self).__init__()

    def reify(self, statement_uri, subject, predicate, object):
        self.add(statement_uri, TYPE, STATEMENT)
        self.add(statement_uri, SUBJECT, subject)
        self.add(statement_uri, PREDICATE, predicate)
        self.add(statement_uri, OBJECT, object)
