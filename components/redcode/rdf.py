import new
from redfoot.xml.handler import HandlerBase

from redfoot.rdf.objects import resource, literal

NS = "http://redfoot.sourceforge.net/2001/09/"
SUBMODULE = resource(NS+"SUBMODULE")
INSTANCE_NAME = resource(NS+"INSTANCE_NAME")
CLASS_NAME = resource(NS+"CLASS_NAME")
FROM = resource(NS+"FROM")

from redfoot.rdf.syntax.parser import RDF_ELEMENT, RDFHandler

class RDFRedcodeRootHandler(HandlerBase):

    def __init__(self, parser, name):
        HandlerBase.__init__(self, parser, None)
        self.name = name
        from redfoot.rednode import RedNode
        uri = 'tmp'
        self.rednode = RedNode(uri)
        self.rednode.local.location = "TODOtmplocation"
        self.rednode.local.uri = uri
        self.globals = {'adder': self.rednode.local.add_statement}

    def child(self, name, atts):
        if name == RDF_ELEMENT:
            RDFHandler(self.parser, self, self.globals)

            app_class = RDFApp

            module = new.module(self.name)
            module.__dict__['_RF_get_app'] = lambda uri, app_class=app_class: app_class(self.rednode)
            self.module = module
        else:
            raise "Did not find expected element '%s'" % RDF_ELEMENT
            #LookForRDFHandler(self.parser, self, self.globals)

    def end(self, name):
        # override HandlerBase
        pass


from redfoot.module import App
class RDFApp(App):
    def __init__(self, rednode):
        self.app = self
        self.rednode = rednode
        self.modules = []
        instance_vars = self.__dict__
        for (instance_name, mod_class) in self.sub_modules():
            mod_instance = mod_class(self)
            instance_vars[instance_name] = mod_instance
            self.modules.append(mod_instance)
        
    def sub_modules(self):
        class SM:
            def __init__(self, rednode=self.rednode):
                self.list = []
                from generic import Generic
                self.list.append(('generic', Generic))
                self.rednode = rednode
            def __call__(self, s, p, o):
                i_n = self.rednode.get_first_value(o, INSTANCE_NAME, None)
                class_name = self.rednode.get_first_value(o, CLASS_NAME, None)
                from_str = self.rednode.get_first_value(o, FROM, None)
                codestr = "from %s import %s" % (from_str, class_name)
                exec codestr+"\n" in globals, locals
                self.list.append([(i_n.value, class_name),])
                
        sm = SM()
        self.rednode.visit(sm, (self.rednode.uri, SUBMODULE, None))
        return sm.list
