#import sys
#sys.path.extend(("../redfoot-core", "../redfoot-components"))

# Needed to be able to import redcode Modules
from redfoot.redcode import importer
importer.install()

# Import Modules you wish to have available
import hello_world, generic #,redfoot_net, grid, foaf, pop, rss, task

# 
from redfoot.rednode import RedNode

#
rednode = RedNode()
rednode.run() # blocks until server is shutdown

