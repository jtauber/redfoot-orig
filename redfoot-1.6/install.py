# Convience script for installing both medusa and redfoot at the same
# time
#
# usage:  python install.py
#            (NOTE: while in this directory)
#

import sys, os

dot = os.path.abspath(os.curdir)
python = sys.executable
args = " ".join(sys.argv[1:])

def run_setup(dir_name):
    os.chdir(dir_name)
    os.system("%s setup.py install %s" % (python, args))
    os.chdir(dot)

# Since 1.5.x is a development series we are going to use import
# dev_hack to find redfootlib etc instead of installing them. As
# setup.py does not have functionality to un-install... etc.
#run_setup("lib")

try:
    import medusa
    print """\
Looks like a version of medusa is already installed...

Warning: Redfoot is only known to work on version of medusa supplied,
namely, 0.5.2 with one patch made to it.

For now, you are on your own updating your version of medusa if
needed.
"""
    
except:
    run_setup("medusa-0.5.2-rf1")


# TODO: would it make sense for this to be a setup.py script as well
# to copy doc and examples somewhere... etc?
