
class Neighbourhood(object):
    def __init__(self, local, neighbours):
        super(Neighbourhood, self).__init__()
        self.local = local
        self.neighbours = neighbours

    def __get_uri(self):
        return self.local.uri
    uri = property(__get_uri)

    def visit(self, callback, triple):
        stop = self.local.visit(callback, triple)
        if stop:
            return stop
        stop = self.neighbours.visit(callback, triple)
        if stop:
            return stop

