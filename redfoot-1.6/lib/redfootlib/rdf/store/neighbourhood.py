from __future__ import generators

from redfootlib.rdf.store.abstract import AbstractStore


class Neighbourhood(AbstractStore):
    def __init__(self, local, neighbours):
        super(Neighbourhood, self).__init__()
        self.local = local
        self.neighbours = neighbours

    def triples(self, s, p, o):
        for triple in self.local.triples(s, p, o):
            yield triple
        for triple in self.neighbours.triples(s, p, o):
            yield triple

