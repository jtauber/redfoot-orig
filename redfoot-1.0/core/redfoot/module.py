from string import rfind
from types import MethodType

class Module:

    def apply_exact(self, path):        
        #print "Module.apply_exact (%s) looking for '%s'" % (self.__class__, path)        
        facet = getattr(self, path, None)
        if facet and type(facet)==MethodType:
            self.app.remaining_path_info = self.app.remaining_path_info[len(path):]
            if path=='':
                self.app.remaining_path_info = None
            elif path[-1]!="/":
                if self.app.remaining_path_info == "":
                    self.app.remaining_path_info = None
            #print "found facet on %s -- leaving: '%s'" % (self.__class__, self.app.remaining_path_info)
            facet()
            return 1

    def apply(self, path=None):
        path = path or self.app.remaining_path_info
        if path or path=='':
            if not self.apply_exact(path):
                self.apply_next(path)

    def apply_next(self, path):
        if not path or path == "":
            return

        if self.app.remaining_path_info == None:
            return

        if path[-1] == "/":
            first = path[:-1]
            if first:
                #print "/ first: '%s'  path: '%s'" % (first, path)
                self.apply(first)
        else:
            pos = rfind(path, "/")
            if pos == -1:
                return

            first = path[:pos+1]
            #print "first: '%s'  path: '%s'" % (first, path)            
            self.apply(first)

# TODO refactor into util.py along with version in rednode.py
def to_URL(module_name, path):
    import sys, urlparse
    from os.path import join, dirname
    from urllib import pathname2url
    if urlparse.urlparse(path)[0] == '':
        libDir = dirname(sys.modules[module_name].__file__)
        return pathname2url(join(libDir, path))
    else: # path is absolute URL
        return path

class ParentModule(Module):

    def apply_exact(self, path, modules=None):
        if not modules:
            if Module.apply_exact(self, path):
                return 1
            module_list = self.modules
        else:
            module_list = modules

        for module in module_list:
            if module.apply_exact(path):
                return 1

    def apply(self, path=None, modules=None):
        path = path or self.app.remaining_path_info
        if path or path=='':
            if not self.apply_exact(path, modules):
                self.apply_next(path)

    def handle_request(self, request, response):
        processor = request.get_parameter('processor', None)
        apply(getattr(self, processor, lambda :None), ())

        for module in self.modules:
            if hasattr(module, 'handle_request'):
                module.handle_request(request, response)


class App(ParentModule):

    def __getattr__(self, name):
        if name=='rednode':
            from redfoot.rednode import RedNode
            rednode = RedNode()
            rdf, uri = ("%s.rdf" % self.__module__, self.URI)
            rednode.load(rdf, uri, 1)
            self.rednode = rednode
            return self.rednode
        elif name=='app':
            self.app = self
            return self
        else:
            raise AttributeError, name

    def handle_request(self, request, response):
        ParentModule.handle_request(self, request, response)

        self.request = request
        self.response = response

        self.app.remaining_path_info = request.get_path_info()
        
        self.apply(self.app.remaining_path_info)

        response.flush()

    def stop(self):
        print "saving rednode"
        self.rednode.local.save()        
