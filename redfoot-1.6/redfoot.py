# Add redfootlib etc to sys.path
import dev_hack

import sys, getopt

from redfootlib.redcmd import RedCmd


def usage():
    print """\
USAGE: redfoot.py <redfoot command file>

    options:
           [-h,--help]

"""    
    sys.exit(-1)


try:
    optlist, args = getopt.getopt(sys.argv[1:], 'h:', ["help"])
except getopt.GetoptError, msg:
    print msg
    usage()

red_cmd = RedCmd()    

argv = sys.argv
for arg in sys.argv[1:]:
    file = open(arg, "r")
    for line in file:
        red_cmd.cmdqueue.append(line)
red_cmd.cmdloop()
