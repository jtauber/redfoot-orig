
class Query(object):
    
    def exists(self, subject, predicate, object):
        for triple in self.triples(subject, predicate, object):
            return 1
        return 0

    def not_exists(self, subject, predicate, object):
        """ TODO: seems like this method is a bit too
        convenient... should # it go away? """
        return not self.exists(subject, predicate, object)

    def get_first_value(self, subject, predicate, default=None):
        for (s, p, o) in self.triples(subject, predicate, None):
            return o
        return default



