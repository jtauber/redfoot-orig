
class HandlerBase:
    def __init__(self, parser, parent):
        self.parser = parser
        self.parent = parent
        self.set_handlers()

    def set_handlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def char(self, data):
        pass

    def child(self, name, atts):
        pass
    
    def end(self, name):
        self.parent.set_handlers()


class IgnoreHandler(HandlerBase):
    def child(self, name, atts):
        print "Ignoring '%s'" % name
        IgnoreHandler(self.parser, self)
