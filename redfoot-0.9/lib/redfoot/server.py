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

    def __init__(self, (host, port), redpage=None):
        Server.__init__(self, ('', port))
        sys.stderr.write("REDFOOT: listening on port %s...\n" % port)
        # TODO localhost might not be the correct thing to use
        sys.stderr.write("... try hitting http://localhost:%s/\n" % port)    
        sys.stderr.flush()
        if port==80:
            self.uri = "http://%s/" % host
        else:
            self.uri = "http://%s:%s/" % (host, port)

        if redpage!=None:
            self.run_autoload(redpage)
        
    def run(self, modulename, *args):
        self._args(modulename, *args)
        self.modulename = modulename
        self._load()
#        self.start()
        try:
            self.keepRunning()
        except KeyboardInterrupt:
            self.stop()

    def run_autoload(self, modulename, *args):
        self._args(modulename, *args)
        self.modulename = modulename
        try:
            self.keepReloading()
        except KeyboardInterrupt:
            self.stop()

    def _args(self, module_name, *args):
        if len(args)==0:
            from redfoot.rednode import RedNode
            node = RedNode()
            rdf_module_name = module_name + ".rdf"

            # TODO: move create if does not exist down further
            import os
            if not os.access(rdf_module_name, os.F_OK):
                node.local.save(rdf_module_name, self.uri)
            
            node.local.load(rdf_module_name, self.uri )
            self._uiargs = (node,)
        else:
            self._uiargs = args

    def _load(self):
        # TODO do we need to worry about passing in globals and locals?
        module = __import__(self.modulename)
        handler = apply(module.UI, self._uiargs)
        self.set_handler(handler)
        self.start()
        return module

    def keepRunning(self):
        while 1:
            threading.Event().wait(100)

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
        sys.stderr.write("Shutting down Redfoot\n")
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
    


import redpage
import os
import __builtin__
real_import = __builtin__.__import__

def _import(name, globals=None, locals=None, fromlist=[]):
    try:
        result = apply(real_import, (name, globals, locals, fromlist))
        return result
    except ImportError, e:
        from string import split, join
        parts = split(name, '.')
        fullname = join(parts, '/')
        location = fullname + ".xml"
        for path in sys.path:
            abs_fullname = "%s/%s" % (path,location)            
            if os.access(abs_fullname, os.F_OK):
                result = redpage.parse_red_page(abs_fullname)
                sys.modules[name] = result
                return result
        raise e
        
__builtin__.__import__ = _import

if __name__ == '__main__':

    import socket
    hostname = socket.getfqdn('localhost')
    port = 80

    import getopt    
    optlist, args = getopt.getopt(sys.argv[1:], 'h:p:')
    if len(args)==0:
        sys.stderr.write("REDFOOT: usage [-h hostname] [-p port] redpage_name\n")
        sys.stderr.flush()
        sys.exit()
        
    for optpair in optlist:
        opt, value = optpair
        if opt=="-h":
            hostname = value
        elif opt=="-p":
            port = string.atoi(value)
    redpage = args[0]
    RedServer((hostname, port), redpage)


#~ $Log$
#~ Revision 8.1  2001/04/29 03:08:02  eikeon
#~ removed old log messages
#~
#~ Revision 8.0  2001/04/27 00:52:13  eikeon
#~ new release
