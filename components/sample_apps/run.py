
try:
    from redfoot.version import VERSION
except ImportError:
    # Try to add redfoot to the path via relative path
    import sys
    sys.path.extend(("../../redfoot-1.1.0/core", ))
    sys.path.extend(("../", ))
    try:
        from redfoot.version import VERSION
        print "Found Redfoot-%s" % VERSION        
    except:
        print "Could not find core Redfoot library"

from redfoot.server.http.daemon import command_line
from redcode.handlers import RedcodeRootHandler

daemon = command_line()
daemon.handlers = {'xml': RedcodeRootHandler}
daemon.run()        
    
