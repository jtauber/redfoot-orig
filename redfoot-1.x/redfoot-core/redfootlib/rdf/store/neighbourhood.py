
class Neighbourhood(object):
    def __init__(self, local, neighbours):
        super(Neighbourhood, self).__init__()
        self.local = local
        self.neighbours = neighbours

    def visit(self, callback, triple):
        stop = self.local.visit(callback, triple)
        if stop:
            return stop
        stop = self.neighbours.visit(callback, triple)
        if stop:
            return stop

