import string, sys, getopt
import os, string

sys.path.append('../core')
sys.path.append('../../tools')

optlist, args = getopt.getopt(sys.argv[1:], 'p:')

if len(args)>0:
    prefix = args[0]
else:
    prefix = 'redfoot'

directory = 'results'
if not os.path.exists(directory):
    os.mkdir(directory)

module_names = []

root_dir = '../core/'
def add_dir(arg, dirname, names):
    # TODO: create abs to rel func
    adir = os.path.abspath(os.path.normpath(root_dir))
    adirname = os.path.abspath(dirname)
    rdirname = adirname[len(adir):]
    
    for name in names:
        add_name(adirname, rdirname, name)

def add_name(adirname, rdirname, name):
    # TODO: clean me up... similar to the prefix comparrison code in coverage.
    # Checking to see if name being added has prefix as its prefix
    ff = os.path.normcase(os.path.abspath(os.path.join(root_dir, prefix)))        
    gg = os.path.normcase(os.path.abspath(os.path.join(adirname, name)))    
    l = [ff, gg]
    if os.path.commonprefix(l)!=ff:
        return
        
    parts = []
    if len(name)>2 and name[-3:]=='.py':
        parts.append(name[:-3])
        
        head = rdirname
        while head:
            head, tail = os.path.split(head)
            if tail:
                parts.append(tail)
            else:
                break

        parts.reverse()
        package_name = string.join(parts, ".")
        module_names.append(package_name)
    
os.path.walk(os.path.join(root_dir, os.path.dirname(prefix)), add_dir, None)


def result(passed, info):
    colour = ['#F00', '#0F0', '#FF0'][passed]
    meaning = ['FAILED', 'PASSED', 'YELLOW'][passed]
    if passed:
        out.write("""
<SPAN STYLE='color:%s'>%s</SPAN>
""" % (colour, meaning))
    else:
        out.write("""
<SPAN STYLE='color:#F00'>FAILED</SPAN>
""")
    out.write("""        
<DD>
%s
</DD>
""" % info)
        

def run():
    out.write("""\
<html>
<body  style="background: #000000; color:#FFFFFF">
<H1>Test Results for core/%s: <a href="../coverage/index.html">(Coverage)</a></H1>
<DL>
""" % prefix)
    for name in module_names:
        out.write("<DT>")
        out.write("""%s <a href="%s.txt">results</a>""" % (name, name))
        
        try:
            when = 'importing'
            m = __import__('test.%s' % name, globals(), locals(), 'run')
            when = 'calling run'
            passed, info = _run(m, name)
        except:
            passed = 0
            exception = sys.exc_info()
            etype, value, tb = sys.exc_info()
            from StringIO import StringIO
            io = StringIO()
            from traceback import print_exception
            print_exception(etype, value, tb, 100*100, io)
            info = """While %s: <pre>%s</pre>""" % (when, io.getvalue())
            
        result(passed, info)
        out.write("</DT>")        
    out.write("""\
</DL>
</body>
</html>
""")

def _run(module, name):
    if hasattr(module, 'run'):
        run = module.run
        fout = open('%s/%s.txt' % (directory, name), 'w')        

        when = 'running'
        sys.stdout = fout
        sys.stderr = fout
        try:
            passed, info = run()
        except:
            # If I let this exception bubble up is was using the wrong
            # 'when'
            passed = 0
            exception = sys.exc_info()
            etype, value, tb = sys.exc_info()
            from StringIO import StringIO
            io = StringIO()
            from traceback import print_exception
            print_exception(etype, value, tb, 100*100, io)
            info = """While %s: <pre>%s</pre>""" % (when, io.getvalue())
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__            
    else:
        passed = 0
        info = "run() not defined"
    return (passed, info)
        
    
def run_with_coverage(run):
    from coverage import Coverage
    coverage = Coverage()
    coverage.start()

    apply(run)

    coverage.end()

    coverage.result(['../core/%s' % prefix,])

out = open('%s/index.html' % directory, 'w')

run_with_coverage(run)
