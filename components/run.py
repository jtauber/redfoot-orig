import sys
sys.path.extend(("../redfoot/core", ))

from redfoot.server.http.daemon import command_line
from redcode.handlers import RedcodeRootHandler

daemon = command_line()
daemon.handlers = {'xml': RedcodeRootHandler}
daemon.run()        
    
