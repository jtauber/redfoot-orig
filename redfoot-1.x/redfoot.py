import sys

def usage():
    print """\
USAGE: redfoot.py <redfoot command file>

    options:
           [-h,--help]

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


if __name__ == "__main__":
    import dev_hack

    import sys, getopt
    from redcmd import RedCmd

    try:
        optlist, args = getopt.getopt(sys.argv[1:],
                                      'h:',
                                      ["help"])
    except getopt.GetoptError, msg:
        print msg
        usage()
    
    red_cmd = RedCmd()    

    argv = sys.argv
    for arg in sys.argv[1:]:
        file = open(arg, "r")
        for line in file:
            line = line.strip()
            # Commands where repeating due to file appear double spaced
            if line:
                red_cmd.cmdqueue.append(line)
    red_cmd.cmdloop()
