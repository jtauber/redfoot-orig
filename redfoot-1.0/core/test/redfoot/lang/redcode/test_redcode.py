from redfoot.redcode.importer import RedcodeModuleImporter
RedcodeModuleImporter().install()

from string import split

# $Header$

#
from redfoot.redcode.parser import parse

# Test1 -- Test for exception when root element is incorrect
try:
    parse('files/test1.xml')
    print "failed test1"
except:
    print "TODO: check for wrong root element exception"

# Test2 -- Test for missing name attribute
try:
    parse('files/test2.xml')
except:
    print "TODO: check that we got the exception we expected"

# Test3 -- 
try:
    module = parse('files/test3.xml')
    print module
    print dir(module)
except:
    import traceback
    traceback.print_exc()
    #sys.stderr.flush()
    #print "failed test3"

# Test4 -- Test redcode importer
#from redcode.importer import RedcodeModuleImporter
#RedcodeModuleImporter().install()

from rc import FooClass
fc = FooClass()
print fc.foo

from inspect import getmodule
print getmodule(FooClass)

import rc

import time
import sys

while 1:
    #print FooClass().foo
    print fc.__class__.foo
    #print sys.modules['rc'].FooClass().foo
    sys.stdout.flush()
    time.sleep(1)



# TODO: add test for off

# $Log$
# Revision 1.1.1.1  2001/08/14 22:29:56  eikeon
# TRANSFER FROM EIKCO
#
# Revision 1.5  2001/06/17 20:16:56  dkrech
# initial
#
# Revision 1.4  2001/06/13 15:25:35  dkrech
# another revision of importer functionality
#
# Revision 1.3  2001/06/11 23:53:39  dkrech
# Rewrote Redcode importer functionaliry
#
# Revision 1.2  2001/06/10 02:37:41  dkrech
# added header log to .py files
#
