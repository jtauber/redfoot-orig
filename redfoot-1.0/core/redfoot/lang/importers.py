from ihooks import ModuleLoader

from sys import modules, stderr
from threading import Thread
from traceback import print_exc
from time import sleep
from os.path import getmtime


class AutoReloadModuleLoader(ModuleLoader):

#    def __init__(self, module_loader):
#        if not isinstance(self, self.hooks.__class__):
#            raise TypeError, "module_loader must be of type ModuleLoader"
#        self.module_loader = module_loader
    def __init__(self):
        ModuleLoader.__init__(self)
        self.importing_modules = {}
        self.mod_info = {}
        self._start()
    
#    def __getattr__(self, name):
#        return getattr(self.module_loader, name)

    def add(self, name, importing_module):
        if not self.importing_modules.has_key(name):
            self.importing_modules[name] = {}
        self.importing_modules[name][importing_module] = 1    

    def load_module(self, name, stuff):
        module = ModuleLoader.load_module(self, name, stuff)
        file, filename, info = stuff

        if filename:
            last = getmtime(filename)
            self.mod_info[name] = (stuff, last)

        return module
    
    def notify(self, module):
        importing_modules = self.importing_modules.get(module.__name__, {})

        for importing_module in importing_modules.keys():
            mod = modules[importing_module]
            func_name = 'notify_me_of_reload'            
            if hasattr(mod, func_name):
                mod.notify_me_of_reload(module)
            else:
                print "%s has changed but %s has no %s function" % (module, mod, func_name)


    def _start(self):
        try:
            import coverage
            import sys
            trace = sys._getframe().f_trace
            target = self._coverage_auto_reload
            args = (trace,)
        except ImportError:
            target = self._auto_reload
            args = ()
        t = Thread(target = target, args = args)
        t.setDaemon(1)
        t.start()
        
    def _coverage_auto_reload(self, trace):
        if trace:
            import sys            
            sys.settrace(trace)
        self._auto_reload()
        
    def _auto_reload(self):        
        while 1:
            sleep(1)
            import sys
            sys.__stdout__.flush()
            sys.__stderr__.flush()            
            for name in self.mod_info.keys():
                stuff, last = self.mod_info[name]
                file, filename, info = stuff

                current = getmtime(filename)            
                if last<current:
                    self.mod_info[name] = (stuff, current)
                    self._reload(name, stuff)

    def _reload(self, name, stuff):
        try:
            file, filename, info = stuff            
            stuff = (open(filename), filename, info)
            module = ModuleLoader.load_module(self, name, stuff)
            modules[name] = module
            self.notify(module)
        except ImportError, msg:
            stderr.write("could not reloaded module '%s'. See the following exception:\n\n" % name)
            #print_exc()
            print msg
            stderr.flush()
                    

from ihooks import ModuleImporter

class AutoReloadModuleImporter(ModuleImporter):
    def __init__(self):
        ModuleImporter.__init__(self)
        self.set_loader(AutoReloadModuleLoader())

    def import_module(self, name, globals={}, locals={}, fromlist=[]):
        importing_module = globals['__name__']

        module = ModuleImporter.import_module(self, name, globals, locals, fromlist)
        self.get_loader().add(module.__name__, importing_module)
        if fromlist:
            for mod_name in fromlist:
                self.get_loader().add("%s.%s" % (module.__name__, mod_name), importing_module)
        return module

