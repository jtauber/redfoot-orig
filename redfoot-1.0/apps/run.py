
import sys
sys.path.extend(("../core", ))
sys.path.extend(("../../components", ))

from redfoot.server.http.daemon import command_line
from redcode.handlers import RedcodeRootHandler
from redcode.rdf import RDFRedcodeRootHandler

daemon = command_line()
daemon.handlers = {'xml': RedcodeRootHandler, 'rdf': RDFRedcodeRootHandler}
daemon.run()        
    
