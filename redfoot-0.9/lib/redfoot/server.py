# $Header$

"""
Redfoot specific server code.
"""

__version__ = "$Revision$"

from bnh.server import Server
import sys
import string

class RedServer(Server):
        

    def keepRunning(self):
        while 1:
            try:
                import threading
                threading.Event().wait(100)
            except KeyboardInterrupt:
                sys.exit()

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
                except:
	            import traceback
                    traceback.print_exc()
                    sys.stderr.flush()
	            import threading
                    threading.Event().wait(1)
                    continue
            
                mtime = getmtime(m.__file__)
                sys.stderr.write("added '%s' @ '%s' '%s'\n" % (m.__name__, mtime, m.__file__))

            if m!=None and getmtime(m.__file__) > mtime+1:
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
                del(sys.modules[modname])
        __builtin__.__import__ = self.realImport
    

if __name__ == '__main__':
    import sys
    redserver = RedServer()
    redserver.runServer(sys.argv[1:])
    from redfoot.editor import PeerEditor

    handler = PeerEditor(redserver.storeNode, redserver.path)
    redserver.server.setHandler(handler)
    redserver.server.start()
    
    redserver.keepRunning()

#~ $Log$
#~ Revision 4.12  2000/12/07 15:58:23  eikeon
#~ removed unused code
#~
#~ Revision 4.11  2000/12/06 23:26:55  eikeon
#~ Made rednode consistently be the local plus neighbourhood; neighbourhood be only the neighbours; and local be only the local part -- much less confusing
#~
#~ Revision 4.10  2000/12/05 03:36:56  eikeon
#~ reordered classes; renamed StoreNode to RedNode
#~
#~ Revision 4.9  2000/12/04 22:00:59  eikeon
#~ got rid of all the getStore().getStore() stuff by using Multiple inheritance and mixin classes instead of all the classes being wrapper classes
#~
#~ Revision 4.8  2000/12/04 05:26:11  eikeon
#~ changed to use new server interface
#~
#~ Revision 4.7  2000/12/04 05:21:24  eikeon
#~ Split server.py into server.py, servlet.py and receiver.py
#~
#~ Revision 4.6  2000/12/04 01:26:44  eikeon
#~ no more getStore() on StoreIO
#~
#~ Revision 4.5  2000/11/08 22:46:42  eikeon
#~ catch and dump exceptions while attempting to load
#~
#~ Revision 4.4  2000/11/07 18:48:40  eikeon
#~ keepReloading now a method on server
#~
#~ Revision 4.3  2000/11/07 18:31:17  eikeon
#~ code to support automatic reloading of handlers... badly needs refactoring
#~
#~ Revision 4.2  2000/11/07 18:20:56  eikeon
#~ fixed bug just introduced
#~
#~ Revision 4.1  2000/11/07 16:55:33  eikeon
#~ factored out creation of handler from runServer
#~
#~ Revision 4.0  2000/11/06 15:57:34  eikeon
#~ VERSION 4.0
#~
#~ Revision 3.4  2000/11/04 01:26:59  eikeon
#~ changed to python 2.0 method of getting the fully qualified domain name... as the 1.6 method in some instances would take a long time
#~
#~ Revision 3.3  2000/11/03 23:04:08  eikeon
#~ Added support for cookies and sessions; prefixed a number of methods and variables with _ to indicate they are private; changed a number of methods to mixed case for consistency; added a setHeader method on response -- headers where hardcoded before; replaced writer with response as writer predates and is redundant with repsonse; Added authentication to editor
#~
#~ Revision 3.2  2000/11/02 21:48:27  eikeon
#~ removed old log messages
#~
# Revision 3.1  2000/10/31 05:03:08  eikeon
# mainly Refactored how parameters are accessed (no more [0]'s); some cookie code; a few minor changes regaurding plumbing
#
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
