from redfoot.lang.importers import AutoReloadModuleImporter
AutoReloadModuleImporter().install()

def notify_me_of_reload(module):
    if module.__name__=='fred':
        print "%s, %s" % (fred, hash(fred))
        fred.testing('asdf')
    else:
        print "RELOADED '%s'" % module        

import sys, time, os

def run():
    print "test"
    from test.redfoot.lang import example_module

    length = 10
    i = length
    while i>0:
        i = i - 1
        print i
        sys.stdout.flush()
        if i==5:
            os.utime(example_module.__file__, None)
            print "touched %s" % example_module.__file__
            sys.stdout.flush()            
        time.sleep(0.5)
    
    return (2, 'TODO: add check for success')

