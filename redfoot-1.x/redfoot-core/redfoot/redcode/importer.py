import exceptions, sys

from ihooks import ModuleImporter, Hooks

from redfoot.redcode.parser import parse
from redfoot.redcode.handlers import RedcodeRootHandler


class RedcodeHooks:

    def __init__(self, hooks):
        self.hooks = hooks
    # Can not figure out a way of making RedcodeHooks of type Hook
    # without it inheriting from Hooks... which we do no want.
    # if not isinstance(self, self.hooks.__class__):
    #     self.__class__ # raise TypeError, "hooks must be of type Hooks"


    def __getattr__(self, name):
        return getattr(self.hooks, name)

    def get_suffixes(self):
        #return self.hooks.get_suffixes() + [('.xml', 'r', 1)]
        return self.hooks.get_suffixes() + [('.xml', 'r', 1), ('.rdf', 'r', 1)]

    def load_source(self, name, filename, file=None):
        from string import split        
        extension = split(filename, '.')[-1]

        handler = self.handlers.get(extension, None)
        if handler:
            try:
                module = parse(file, name, handler)
                sys.modules[name] = module                
                # TODO: close file?
                return module
            except exceptions.SyntaxError, err:
                msg = "%s: %s" % (filename, err)
                raise ImportError(msg)
            else:
                if file:
                    file.close()
        else:
            return self.hooks.load_source(name, filename, file)


class RedcodeModuleImporter(ModuleImporter):        
    """
    Importer that imports Redcode Modules in addtion to what
    ModuleImporter normally imports.

    Example:    
      RedcodeModuleImporter().install()
      import foo
    """
    
    def __init__(self, handlers={'xml': RedcodeRootHandler}):
        ModuleImporter.__init__(self)
        rh = RedcodeHooks(self.get_hooks())
        if handlers==None:
            from redfoot.redcode.handlers import RedcodeRootHandler
            handlers = {'xml': RedcodeRootHandler}
        rh.handlers = handlers
        self.set_hooks(rh)

def install():
    # TODO: add check for it already being installed
    importer = RedcodeModuleImporter()
    importer.install()
