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


run_setup("redfoot-core")
run_setup("redfoot-components")

try:
    import medusa
    print """\
Warning: Redfoot is only known to work on version of medusa supplied, namely, 0.5.2 with one patch made to it.

For now, you are on your own updating your version of medusa if needed.
"""
except:
    run_setup("medusa-0.5.2-rf1")


# TODO: would it make sense for this to be a setup.py script as well
# to copy redfoot-doc and redfoot-examples somewhere... etc?
