import sys

try:
    from redfoot.version import VERSION
except ImportError:
    # Try to add redfoot to the path via relative path
    sys.path.extend(("../../redfoot-1.1.0/core", ))
    try:
        from redfoot.version import VERSION
        print "Found Redfoot-%s" % VERSION        
    except:
        print "Could not find core Redfoot library"

# add components directory to PYTHONPATH
sys.path.extend(("../", ))
    
from redfoot.server.http.daemon import command_line
from redcode.handlers import RedcodeRootHandler

daemon = command_line()
daemon.handlers = {'xml': RedcodeRootHandler}
daemon.run()        
    
