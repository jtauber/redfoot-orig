import string, sys
from getopt import getopt as get_options, GetoptError

def process_args():
    uri = None
    rdf = "rednode.rdf"    
    address = ''
    port = 8080
    
    try:
        optlist, args = get_options(sys.argv[1:],
                                    'u:h:a:p:r:',
                                    ["uri=", "help", "address=",
                                     "port=", "rdf="])
    except GetoptError, msg:
        print msg
        usage()
    
    for optpair in optlist:
        opt, value = optpair
        if opt=="-u" or opt=="--uri":
            uri = value
        elif opt=="-h" or opt=="--help":            
            usage()
        elif opt=="-a" or opt=="--address":
            address = value
        elif opt=="-p" or opt=="--port":
            port = string.atoi(value)
        elif opt=="-r" or opt=="--rdf":
            rdf = value
        else:
            usage()

    if not uri:
        from socket import getfqdn
        hostname = getfqdn()
        if port==80:
            uri = "http://%s/" % hostname
        else:
            uri = "http://%s:%s/" % (hostname, port)
        uri = uri

    # Needed to be able to import redcode Modules
    from redfoot.redcode import importer
    importer.install()

    if len(args)==0:
        usage()
        sys.exit(-1)
        
    for arg in args:
        if len(arg)>4 and arg[-4:] == ".xml":
            arg = arg[:-4]
        elif len(arg)>3 and arg[-3:] == ".py":
            arg = arg[:-3]
        try:
            __import__(arg)
        except ImportError:
            print """
Error: Could not import '%s'

  %s %s --help for command line options

""" % (arg, sys.executable, sys.argv[0])
            sys.exit(-1)
    return (uri, rdf, address, port)


def usage():
    print """\
USAGE: run.py <options> <app name>

    options:
           [-u,--uri <uri>]
           [-r,--rdf <filename>]
           [-a,--address <address>]
           [-p,--port <port number>]
           [-h,--help]

    uri
        Defaults to a computed URI using socket's getfqdn call
    rdf
        Defaults to rednode.rdf
    address
        Defaults to listening on all addresses 
    port
        Defaults to 8080.
"""    
    sys.exit(-1)


if not hasattr(sys, 'version_info') or sys.version_info[0]<2:
    print """\
Can not run redfoot with Python verion:
  '%s'""" % sys.version
    print "Redfoot requires Python 2.0 or higher to run. "
    sys.exit(-1)
else:
    if sys.version_info[1]<2:
        print """\
Warning: Redfoot not tested or known to run with Python version less than 2.2
"""
    elif sys.version_info[2]<1:
        print """\
Warning: Redfoot requires a bug fix from 2.2.1 in order to run correctly
"""
        

try:
    import threading
except ImportError:
    print """
Redfoot can not run without the threading module. Check that your PYTHONPATH is right and that you have threading.py
"""
    sys.exit(-1)
