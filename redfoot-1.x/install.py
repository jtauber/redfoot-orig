# Convience script for installing both medusa and redfoot at the same
# time
import sys, os

dot = os.path.abspath(os.curdir)
python = sys.executable
args = " ".join(sys.argv[1:])

def run_setup(dir_name):
    os.chdir(dir_name)
    os.system("%s setup.py install %s" % (python, args))
    os.chdir(dot)

# TODO: first check to see if they already have a version of medusa
# install. If so, let them install individually on their own.
run_setup("medusa")

run_setup("redfoot-core")
run_setup("redfoot-components")

# TODO: would it make sense for this to be a setup.py script as well
# to copy redfoot-doc and redfoot-examples somewhere... etc?
