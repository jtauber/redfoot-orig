import sys
sys.path.extend(("../redfoot-core", "../redfoot-components"))

# 
from redfoot.rednode import RedNode

#
rednode = RedNode()
rednode.run() # blocks until server is shutdown

