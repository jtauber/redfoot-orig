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
        

    def keepReloading(self, lm):
        from os.path import getmtime
        rollbackImporter = None
        m = None
        while 1:
            if m==None:
                if rollbackImporter:
                    rollbackImporter.uninstall()
                rollbackImporter = RollbackImporter()
        
                try:
                    m = lm(self)
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
                else:
                    #sys.stderr.write("did not have key for module %s\n" % modname)
                #sys.stderr.flush()
        __builtin__.__import__ = self.realImport
    

#~ $Log$
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
