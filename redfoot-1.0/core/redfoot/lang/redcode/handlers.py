import new
import string

from redfoot.xml.handler import HandlerBase

NS = "http://redfoot.sourceforge.net/2001/06/^"
MODULE = NS+"module"
CLASS = NS+"class"


class RedcodeHandler(HandlerBase):

    def __init__(self, parser):
        HandlerBase.__init__(self, parser, None)

    def child(self, name, atts):
        if name==MODULE:
            if atts.has_key('name'):
                module_name = atts['name']
            else:
                raise "Module does not have required name attribute"
            rfch = ModuleHandler(self.parser, self, module_name)
            self.module = rfch.module            
        else:
            raise str("did not find a '%s' root element... instead found '%s'" % (MODULE, name))

    def end(self, name):
        # override HandlerBase
        pass


class ModuleHandler(HandlerBase):

    def __init__(self, parser, parent, name):
        HandlerBase.__init__(self, parser, parent)
        self.module = new.module(name)
        self.globals = self.module.__dict__
        self.locals = self.globals
        self.codestr = ""

    def child(self, name, atts):
        codestr = self.codestr
        if codestr!="":
            exec codestr+"\n" in self.globals, self.locals
            self.codestr = ""
        if name==CLASS:
            if atts.has_key('bases'):
                bases = "(" + string.join(string.split(atts['bases']),",") + ",)"
                base_classes = eval(bases, self.globals, self.locals)
            else:
                base_classes = ()
            eh = ClassHandler(self.parser, self, atts['name'], base_classes)
            classobj = eh.classobj
            module = self.module
            classobj.__module__ = module.__name__
            module.__dict__[classobj.__name__] = classobj
        else:
            raise "Ignoring unexpeced element '%s'\n" % name

    def char(self, data):
        self.codestr = self.codestr + data

    def end(self, name):
        HandlerBase.end(self, name)
        exec self.codestr+"\n" in self.globals, self.locals


class ClassHandler(HandlerBase):

    def __init__(self, parser, parent, name, base_classes):
        HandlerBase.__init__(self, parser, parent)

        self.classobj = new.classobj(name.encode('ascii'), base_classes, {})
        self.locals = self.classobj.__dict__
        self.globals = self.parent.locals
        self.codestr = ""
            
    def child(self, name, atts):
        raise "Ignoring unexpected element '%s'\n" % name

    def char(self, data):
        self.codestr = self.codestr + data

    def end(self, name):
        HandlerBase.end(self, name)
        exec self.codestr+"\n" in self.globals, self.locals

