print 'fred'

import sys


def run():
    print "running all tests for core"

    from coverage import Coverage
    coverage = Coverage()
    coverage.start()
    #run()
    sys.stdout.write("Test of Server... control-c to continue other tests.\n")
    sys.stdout.flush()
    from test.redfoot.server import all

    from test.redfoot.rdf.syntax import test
    from test.redfoot.rdf.syntax import test2

    from test.redfoot.rdf.store import test    

    sys.settrace(None)#coverage.end()
    
    import os
    contains = os.path.normpath('redfoot')
    print "CONTAINS" + contains
    coverage.result([contains,], open('coverage.html', 'w'))



packages = ['lang',]
#      #redfoot = __import__('redfoot')
#      for package in packages:
#          all = __import__('redfoot.%s.test.all' % package, globals(), locals(), ['redfoot'])
#          all.run()

