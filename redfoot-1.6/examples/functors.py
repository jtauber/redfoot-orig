# TODO: document!
# candidate to move into core

class slice:
    def __init__(self, callback, start=None, end=None):
        self.callback = callback
        self.start = start
        self.end = end
        self.i = 0

    def __call__(self, *args):
        if not (self.start and self.i<self.start):
            if not (self.end and self.i>self.end):
                apply(self.callback, args)
        self.i = self.i + 1

