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

    for arg in args:
        __import__(arg)
    
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


try:
    import threading
except ImportError:
    print """
Redfoot can not run without the threading module. Check that your PYTHONPATH is right and that you have threading.py
"""
    sys.exit(-1)
