def usage():
    print "USAGE: run.py <module name>"
    sys.exit(-1)
    
import string, sys, getopt

sys.path.extend(('../core', '../components'))

# set default value
port = 8000
optlist, args = getopt.getopt(sys.argv[1:], 'p:')
for optpair in optlist:
    opt, value = optpair
    if opt=="-p":
        port = string.atoi(value)

if len(args)!=1:
    usage()

module = args[0]

if module[-4:] == ".xml":
    module = module[:-4]

from redfoot.server.http.daemon import RedDaemon
from redcode.handlers import RedcodeRootHandler

daemon = RedDaemon(('localhost', port), module, RedcodeRootHandler)

try:
    daemon.run()
except ImportError, msg:
    print "%s: %s" % (msg.__class__.__name__, msg)
    