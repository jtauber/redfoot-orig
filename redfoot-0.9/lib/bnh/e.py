#! /usr/bin/env python

import __builtin__
import string
import sys

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
                del(sys.modules[modname])
        __builtin__.__import__ = self.realImport
    

def testing(lm):
    # set default value
    port = 8000
        
    import getopt
    optlist, args = getopt.getopt(sys.argv[1:], 'p:')
    for optpair in optlist:
        opt, value = optpair
        if opt=="-p":
            port = string.atoi(value)
            
    server = Server(('', port))
    server.start()

    sys.stderr.write("EXAMPLE: serving requests on port %s...\n" % port)
    sys.stderr.flush()

    from os.path import getmtime
    rollbackImporter = None
    m = None
    while 1:
        if m==None:
            if rollbackImporter:
                rollbackImporter.uninstall()
            rollbackImporter = RollbackImporter()
        
            m = lm(server)
            
            mtime = getmtime(m.__file__)
            sys.stderr.write("added '%s' @ '%s'\n" % (m.__name__, mtime))

        if getmtime(m.__file__) > mtime+1:
            handler = m.h
            if handler!=None:
                handler.stop()
                sys.stderr.write("removed '%s' @ '%s'\n" % (m.__name__, mtime))
                m = None
            else:
                sys.stderr.write("'%s': '%s' -- '%s'\n" % (m.__file__, getmtime(m.__file__), mtime))
        
        sys.stderr.flush()
        import threading
        threading.Event().wait(1)


def fred(server):
    import example
    handler = server.addHandler(example.ExampleHandler())
    example.h = handler
    return example


testing(fred)
