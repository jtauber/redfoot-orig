#
import sys

if not hasattr(sys, 'version_info') or sys.version_info[0]<2:
    print """\
Can not run redfoot with Python verion:
  '%s'""" % sys.version
    print "Redfoot requires Python 2.2.1 or higher to run. "
    sys.exit(-1)
else:
    if sys.version_info[1]<2:
        print "Redfoot requires Python 2.2.1 or higher to run. "
        sys.exit(-1)
    elif sys.version_info[2]<1:
        print "Redfoot requires Python 2.2.1 or higher to run. "
        sys.exit(1)

# TODO: Test does not work... as it finds redfootlib.xml instead :(
# try:
#     import xml.parsers.expat
# except:
#     print """\
# Could not import xml.parsers.expat which Redfoot requires.
# """
#     sys.exit(-1)

try:
    import threading
except ImportError:
    print """\
Redfoot can not run without the threading module. Check that your PYTHONPATH is right and that you have threading.py
"""
    sys.exit(-1)

