# Convience script for installing both medusa and redfoot at the same
# time

import sys, os

python = sys.executable
args = " ".join(sys.argv[1:])

# TODO: first check to see if they already have a version of medusa
# install. If so, let them install individually on their own.
os.system("%s medusa/setup.py install %s" % (python, args))

os.system("%s redfoot-core/setup.py install %s" % (python, args))
os.system("%s redfoot-components/setup.py install %s" % (python, args))

# TODO: would it make sense for this to be a setup.py script as well
# to copy redfoot-doc and redfoot-examples somewhere... etc?
