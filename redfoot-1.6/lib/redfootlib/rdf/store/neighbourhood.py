from __future__ import generators


class Neighbourhood(object):
    def __init__(self, local, neighbours):
        super(Neighbourhood, self).__init__()
        self.local = local
        self.neighbours = neighbours

    def __get_uri(self):
        return self.local.uri
    uri = property(__get_uri)

    def triples(self, s, p, o):
        for triple in self.local.triples(s, p, o):
            yield triple
        for triple in self.neighbours.triples(s, p, o):
            yield triple

    def subjects(self, p, o):
        for subject in self.local.subjects(p, o):
            yield subject
        for subject in self.neighbours.subjects(p, o):
            yield subject

    def objects(self, s, p):
        for object in self.local.objects(s, p):
            yield object
        for object in self.neighbours.objects(s, p):
            yield object

    def visit(self, callback, triple):
        stop = self.local.visit(callback, triple)
        if stop:
            return stop
        stop = self.neighbours.visit(callback, triple)
        if stop:
            return stop

