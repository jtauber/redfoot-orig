if __name__ == '__main__':
    import sys
    from redfoot.server import RedServer

    port = 8000
    import getopt
    import sys
    optlist, args = getopt.getopt(sys.argv[1:], 'p:')
    for optpair in optlist:
        opt, value = optpair
        if opt=="-p":
	    import string
            port = string.atoi(value)
            

    def load(server):
        import sample1
        handler = sample1.Sample1UI()
        server.set_handler(handler)
        server.start()
        return sample1

    redserver = RedServer(('', port))
    sys.stderr.write("Sample1: listening on port %s...\n" % port)
    sys.stderr.write("... try hitting http://localhost:%s/\n" % port)    
    sys.stderr.flush()
    try:
        redserver.keepReloading(load)
    except KeyboardInterrupt:
        sys.stderr.write("Shutting down Sample1\n")
        sys.stderr.flush()

        redserver.stop()
