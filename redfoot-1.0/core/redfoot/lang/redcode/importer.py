from redfoot.lang.redcode.parser import parse

# TODO: revisit relation to redfoot.lang.redcode.importers
from ihooks import Hooks
import exceptions, sys

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
        return self.hooks.get_suffixes() + [('.xml', 'r', 1)]

    def load_source(self, name, filename, file=None):
        from string import split        
        extension = split(filename, '.')[-1]

        if extension=="xml":
            try:
                module = parse(file, name, self.handler_class)
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

        
from redfoot.lang.importers import AutoReloadModuleImporter

class RedcodeModuleImporter(AutoReloadModuleImporter):    
    """
    Importer that imports Redcode Modules in addtion to what
    ModuleImporter normally imports.

    Example:    
      RedcodeModuleImporter().install()
      import foo
    """
    
    def __init__(self, handler_class):
        AutoReloadModuleImporter.__init__(self)
        rh = RedcodeHooks(self.get_hooks())
        rh.handler_class = handler_class
        self.set_hooks(rh)

