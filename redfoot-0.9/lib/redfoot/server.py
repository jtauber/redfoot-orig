# $Header$

"""
Redfoot specific server code.
"""

__version__ = "$Revision$"

from bnh.server import Server
import sys
import string
import threading

class RedServer(Server):

    def __init__(self, (host, port)):
        Server.__init__(self, (host, port))
        sys.stderr.write("REDFOOT: listening on port %s...\n" % port)
        # TODO localhost might not be the correct thing to use
        sys.stderr.write("... try hitting http://localhost:%s/\n" % port)    
        sys.stderr.flush()

    def run(self, modulename, *args):
        self._uiargs = args
        self.modulename = modulename
        self._load()
        self.start()
        try:
            self.keepRunning()
        except KeyboardInterrupt:
            self.stop()

    def run_autoload(self, modulename, *args):
        self._uiargs = args
        self.modulename = modulename
        try:
            self.keepReloading()
        except KeyboardInterrupt:
            self.stop()

    def run_redpage(self, location, *args):
        self._uiargs = args
        self.location = location
        self._load = self._load_redpage
        try:
            self.keepReloading()
        except KeyboardInterrupt:
            self.stop()
    
    def _load(self):
        # TODO do we need to worry about passing in globals and locals?
        module = __import__(self.modulename)
        handler = apply(module.UI, self._uiargs)
        self.set_handler(handler)
        self.start()
        return module

    def _load_redpage(self):
        import redpage
        module = redpage.parse_red_page(self.location)
        module.__file__ = self.location
        handler = apply(module.UI, self._uiargs)
        self.set_handler(handler)
        self.start()
        return module

    def keepRunning(self):
        while 1:
            try:
                threading.Event().wait(100)
            except KeyboardInterrupt:
                sys.exit()

    def _getFilename(self, module):
        file = module.__file__
        if file[-3:]=="pyc":
            file = file[:-1]
        return file

    def keepReloading(self):
        from os.path import getmtime
        rollbackImporter = None
        m = None
        while 1:
            if m==None:
                if rollbackImporter:
                    rollbackImporter.uninstall()
                rollbackImporter = RollbackImporter()
        
                try:
                    m = self._load()
                    filename = self._getFilename(m)
                except:
	            import traceback
                    traceback.print_exc()
                    sys.stderr.flush()
                    threading.Event().wait(1)
                    continue
            
                mtime = getmtime(filename)
                sys.stderr.write("added '%s' @ '%s' '%s'\n" % (m.__name__, mtime, filename))
                sys.stderr.flush()

            if m!=None and getmtime(filename) > mtime+1:
                if self.handler!=None:
                    self.stop()
                    sys.stderr.write("removed '%s' @ '%s'\n" % (m.__name__, mtime))
                    sys.stderr.flush()
                    m = None
                else:
                    sys.stderr.write("'%s': '%s' -- '%s'\n" % (filename, getmtime(filename), mtime))
                    sys.stderr.flush()
            else:
                threading.Event().wait(1)

    def stop(self):
        sys.stderr.write("Shutting down Sample1\n")
        sys.stderr.flush()
        Server.stop(self)



import string
import sys
import __builtin__

from redfoot.server import Server

class RollbackImporter:
    def __init__(self):
        "Creates an instance and installs as the global importer"
        self.rollbackImporter = None
        self.previousModules = sys.modules.copy()
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import
        self.newModules = {}
        
    def _import(self, name, globals=None, locals=None, fromlist=[]):
        result = apply(self.realImport, (name, globals, locals, fromlist))
        self.newModules[name] = 1
        return result
        
    def uninstall(self):
        for modname in self.newModules.keys():
            if not self.previousModules.has_key(modname):
                # Force reload when modname next imported
                if sys.modules.has_key(modname):
                    #sys.stderr.write("deleting module %s\n" % modname)
                    del(sys.modules[modname])
                #else:
                    #sys.stderr.write("did not have key for module %s\n" % modname)
                #sys.stderr.flush()
        __builtin__.__import__ = self.realImport
    

#~ $Log$
#~ Revision 6.3  2001/03/26 20:20:42  eikeon
#~ added run_redpage and _load_redpage
#~
#~ Revision 6.2  2001/03/22 01:10:27  jtauber
#~ refactor of apps and the way servers are started by them
#~
#~ Revision 6.1  2001/02/26 22:41:03  eikeon
#~ removed old log messages
#~
#~ Revision 6.0  2001/02/19 05:01:23  jtauber
#~ new release
