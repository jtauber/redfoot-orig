import string, sys, getopt, os

def usage():
    print """\
USAGE: run.py <options> <module name>

    options:
           [-h,--hostname <host name>]
           [-p,--port <port number>]
           [--exact]
           [--help]

    hostname
        Defaults to the computers fully qualified name. 
    port
        Defaults to 8000.
    exact
        Defaults to false.
        If true, listen to request coming to host via the exact host name only. Else listens to request coming to host via any of its names.
"""    
    sys.exit(-1)


if not hasattr(sys, 'version_info') or sys.version_info[0]<2:
    print """\
Can not run redfoot with Python verion:
  '%s'""" % sys.version
    print "Redfoot requires Python 2.0 or higher to run. "
    sys.exit(-1)


try:
    import threading
except ImportError:
    print """
Can not run redfoot without threading module. 
"""
    sys.exit(-1)
    

RF_HOME = ".." + os.sep
sys.path.extend((RF_HOME + "core", RF_HOME + "components"))

# set default value
port = 8000
exact = 0
hostname = None

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'p:h:', ["help", "exact", "port=", "hostname="])
except getopt.GetoptError, msg:
    print msg
    usage()
    
for optpair in optlist:
    opt, value = optpair
    if opt=="-p" or opt=="--port":
        port = string.atoi(value)
    elif opt=="-h" or opt=="--hostname":
        hostname = value
    elif opt=="--exact":
        exact = 1
    elif opt=="--help":
        usage()

if not hostname:
    from socket import getfqdn
    hostname = getfqdn()

if len(args)<1:
    usage()

module = args[0]

# Be forgiving if the module file name was specified instead of just
# the module name
if module[-4:] == ".xml":
    module = module[:-4]

from redfoot.server.http.daemon import RedDaemon
from redcode.handlers import RedcodeRootHandler

daemon = RedDaemon((hostname, port), module, RedcodeRootHandler, exact)
daemon.run()        
    
