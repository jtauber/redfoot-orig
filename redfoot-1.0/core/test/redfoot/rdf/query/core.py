from redfoot.rdf.store import triple
from redfoot.rdf.objects import resource, literal

from redfoot.rdf.query.functors import *
from redfoot.rdf.query.core import *
from redfoot.rdf.query.builders import *

def compare_lists(list1, list2):
    for item in list1:
        if not item in list2:
            return 0
    for item in list2:
        if not item in list1:
            return 0
    return 1

class QueryStore(Query, triple.TripleStore):
    pass

def run():

    passed = 0

    store = QueryStore()

    store.add(resource("john"), resource("age"), literal("37"))
    store.add(resource("paul"), resource("age"), literal("35"))
    store.add(resource("peter"), resource("age"), literal("35"))

    b = ItemBuilder()

    store.visit(triple2statement(b.accept), (None, resource("age"), None))
    if b.item.subject == resource("john"):
        print "passed 1"
        passed = passed + 1
    else:
        print "failed 1"

    b = ListBuilder()

    l = []
    store.visit(triple2statement(b.accept), (None, resource("age"), None))
    for st in b.list:
        l.append((str(st.subject), str(st.predicate), str(st.object)))

    correct = [('peter', 'age', '35'), ('paul', 'age', '35'), ('john', 'age', '37')]
    if compare_lists(l, correct):
        print "passed 2"
        passed = passed + 1
    else:
        print "failed 2. got", l

    b = ListBuilder()

    l = []
    store.visit(triple2statement(b.accept), (None, resource("age"), literal("35")))
    for st in b.list:
        l.append((str(st.subject), str(st.predicate), str(st.object)))

    correct = [('peter', 'age', '35'), ('paul', 'age', '35')]
    if compare_lists(l, correct):
        print "passed 3"
        passed = passed + 1
    else:
        print "failed 3. got", l

    class TestResult:
        def __init__(self):
            self.result = []

        def add_list(self, *args):
            self.result.append(map(str, args))

        def add_list2(self, *args):
            a = map(lambda x: "-" + str(x), args)
            self.result.append(a)

    t = TestResult()
    store.visit(t.add_list, (None, resource("age"), None))
    correct = [['peter', 'age', '35'], ['paul', 'age', '35'], ['john', 'age', '37']]
    if compare_lists(t.result, correct):
        print "passed 4"
        passed = passed + 1
    else:
        print "failed 4"

    t = TestResult()
    store.visit(so(t.add_list), (None, resource("age"), None))
    correct = [['peter', '35'], ['paul', '35'], ['john', '37']]
    if compare_lists(t.result, correct):
        print "passed 5"
        passed = passed + 1
    else:
        print "failed 5"

    t = TestResult()
    store.visit(both(t.add_list, t.add_list2), (None, resource("age"), None))
    correct = [['peter', 'age', '35'], ['-peter', '-age', '-35'], ['paul', 'age', '35'], ['-paul', '-age', '-35'], ['john', 'age', '37'], ['-john', '-age', '-37']]
    if compare_lists(t.result, correct):
        print "passed 6"
        passed = passed + 1
    else:
        print "failed 6"

    t = TestResult()
    store.visit(first(t.add_list), (None, resource("age"), None))
    correct = [['peter', 'age', '35']]
    if compare_lists(t.result, correct):
        print "passed 7"
        passed = passed + 1
    else:
        print "failed 7"

    if store.exists(resource("john"), resource("age"), literal("37")):
        print "passed 8"
        passed = passed + 1
    else:
        print "failed 8"

    if not store.exists(resource("john"), resource("age"), literal("36")):
        print "passed 9"
        passed = passed + 1
    else:
        print "failed 9"

    def filter1(s, p, o):
        return s == resource("john")

    t = TestResult()
    store.visit(filter(t.add_list, filter1), (None, None, None))
    correct = [['john', 'age', '37']]
    if compare_lists(t.result, correct):
        print "passed 10"
        passed = passed + 1
    else:
        print "failed 10"

    if passed == 10:
        return (1, "ALL TESTED PASSED")
    elif passed > 1:
        return (0, "ONLY %s TESTS PASSED" % passed)
    elif passed == 1:
        return (0, "ONLY 1 TEST PASSED")
    else:
        return (0, "NO TESTS PASSED")
        
