
class ReificationStore:
    """Mixin to enable reification."""
    
    def reify(self, statement_uri, subject, predicate, object):
        self.add(statement_uri, TYPE, STATEMENT)
        self.add(statement_uri, SUBJECT, subject)
        self.add(statement_uri, PREDICATE, predicate)
        self.add(statement_uri, OBJECT, object)
