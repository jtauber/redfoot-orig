from redfoot.rdf.store.triple import TripleStore

ts = TripleStore()

class Counter:

    def __init__(self):
        self.count = 0

    def visit(self, s, p, o):
        self.count = self.count + 1
        return 0

class Stop:

    def __init__(self):
        self.count = 0

    def visit(self, s, p, o):
        self.count = self.count + 1
        return 1

def test((s, p, o), expected):
    t = {'args': "(%s, %s, %s)" % (s, p, o), 'expected': "%s" % expected}

    cstr = """\
info = ''
stop = Stop()
r = ts.visit(stop.visit, %(args)s)
if expected>0 and stop.count!=1:
    passed = 0
    info = "Found '%%s' expected 1" %% stop.count
    
counter = Counter()
r = ts.visit(counter.visit, %(args)s)
if counter.count!=%(expected)s:
    passed = 0
    info = info + "<pre>Found '%%s' expected %(expected)s when testing visit(callback, %(args)s)</pre>" %% counter.count
""" % t    
        
    exec cstr
    return info

def run():
    passed = 1
    info = ''

    foo = "s1"
    for s in ['s%s' % i for i in [1, 2, 3]]:
        for p in ['p%s' % i for i in [1, 2, 3]]:
            for o in ['o%s' % i for i in [1, 2, 3]]:                    
                ts.add(s, p, o)

    # Nothing specified
    info = info + test(("None", "None", "None"), 27) + "\n"

    # One coordinates specified
    for i in [1, 2, 3]:
        for first in [0, 1, 2]:
            for second in [x for x in [0, 1, 2] if x!=first]:
                third = [x for x in [0, 1, 2] if x!=first and x!=second][0]                
                triple = [None, None, None]
                triple[first] = "'%s%i'" % (['s', 'p', 'o'][first], i)
                triple[second] = "None"
                triple[third] = "None"

                triple_1 = (triple[0], triple[1], triple[2])                                

                triple[second] = "'object not in triple store'"
                triple_2 = (triple[0], triple[1], triple[2])

                triple[first] = "'object not in triple store'"
                triple[second] = "None"                                
                triple_3 = (triple[0], triple[1], triple[2])                
                    
                info = info + test(triple_1, 9) + "\n"
                info = info + test(triple_2, 0) + "\n"                
                info = info + test(triple_3, 0) + "\n"                

    # Two coordinates specified
    for i in [1, 2, 3]:
        for j in [1, 2, 3]:
            for first in [0, 1, 2]:
                for second in [x for x in [0, 1, 2] if x!=first]:
                    third = [x for x in [0, 1, 2] if x!=first and x!=second][0]
                    triple = [None, None, None]
                    triple[first] = "'%s%i'" % (['s', 'p', 'o'][first], i)
                    triple[second] = "'%s%i'" % (['s', 'p', 'o'][second], j)
                    triple[third] = "None"
                    triple_1 = (triple[0], triple[1], triple[2])
                    triple[third] = "'object not in triple store'"
                    triple_2 = (triple[0], triple[1], triple[2])                    
                    info = info + test(triple_1, 3) + "\n"
                    info = info + test(triple_2, 0) + "\n"                    

    
    # Test of all fully specified queries
    for s in ['s%s' % i for i in [1, 2, 3]]:
        for p in ['p%s' % i for i in [1, 2, 3]]:
            for o in ['o%s' % i for i in [1, 2, 3]]:
                info = info + test(("'%s'" % s, "'%s'" % p, "'%s'" % o), 1) + "\n"                            


    counter = Counter()
    r = ts.visit_subjects(counter.visit)
    if counter.count!=3:
        passed = 0        
        info = info + "visit_subjects returned %s but expected 3 subjects" % counter.count

    ts.remove(None, None, None)
    


    return (passed, info)

