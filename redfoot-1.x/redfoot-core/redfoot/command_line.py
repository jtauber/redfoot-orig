import string, sys
from getopt import getopt as get_options, GetoptError

def process_args():
    uri = None
    port = 8080
    rdf_filename = "rednode.rdf"
    
    try:
        optlist, args = get_options(sys.argv[1:],
                                    'u:h:p:r:',
                                    ["uri=", "help", "port=", "rdf="])
    except GetoptError, msg:
        print msg
        usage()
    
    for optpair in optlist:
        opt, value = optpair
        if opt=="-u" or opt=="--uri":
            uri = value
        elif opt=="-h" or opt=="--help":            
            usage()
        elif opt=="-p" or opt=="--port":
            port = string.atoi(value)
        elif opt=="-r" or opt=="--rdf":
            rdf_filename = value
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
    
    return (uri, rdf_filename, port)


def usage():
    print """\
USAGE: run.py <options> <app name>

    options:
           [-h,--hostname <host name>]
           [-p,--port <port number>]
           [--exact]
           [--help]

    hostname
        Defaults to the computer's fully qualified name. 
    port
        Defaults to 8000.
    exact
        If exact server will listen to request coming to host via the exact host name only. Else listens to all request coming to host regaurdless of what name they come in on.
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
