import string, sys, getopt

# set default value
port = 8000
optlist, args = getopt.getopt(sys.argv[1:], 'p:')
for optpair in optlist:
    opt, value = optpair
    if opt=="-p":
        port = string.atoi(value)


from redfoot.server.http.daemon import RedDaemon
daemon = RedDaemon(('', port), 'test.redfoot.server.test_redpages')

daemon.run()
