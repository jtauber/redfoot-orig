import sys
sys.path.extend(("../../redfoot-1.1/core", ))
sys.path.extend(("../", ))

from redfoot.server.http.daemon import command_line
from redcode.handlers import RedcodeRootHandler

daemon = command_line()
daemon.handlers = {'xml': RedcodeRootHandler}
daemon.run()        
    
