from redfoot.rdf.store import triple
from redfoot.rdf.objects import resource, literal
from redfoot.rdf.query.builders import *
from redfoot.rdf.query.functors import *

def run():

    passed = 0

    store = triple.TripleStore()

    store.add(resource("john"), resource("age"), literal("37"))
    store.add(resource("paul"), resource("age"), literal("35"))
    store.add(resource("peter"), resource("age"), literal("35"))

    b = StatementBuilder()
    store.visit(b.accept, (None, resource("age"), literal("37")))

    if b.statement.subject == resource("john"):
        print "passed 1"
        passed = passed + 1
    else:
        print "failed 1"

    b = ListBuilder()
    store.visit(o(b.accept), (None, None, None))

    def my_comparator(a, b):
        if a.value < b.value:
            return -1
        elif a.value == b.value:
            return 0
        else:
            return 1

    b.sort(my_comparator)

    if b.list == [literal("35"), literal("35"), literal("37")]:
        print "passed 2"
        passed = passed + 1
    else:
        print "failed 2"

    def my_filter(a):
        if int(a.value) > 36:
            return 1
        else:
            return 0

    b = ListBuilder()
    store.visit(o(b.accept), (None, None, None))

    b.filter(my_filter)
    
    if b.list == [literal("37")]:
        print "passed 3"
        passed = passed + 1
    else:
        print "failed 3: get", b.list

    b = SetBuilder()
    store.visit(o(b.accept), (None, None, None))

    b.sort(my_comparator)

    if b.set == [literal("35"), literal("37")]:
        print "passed 4"
        passed = passed + 1
    else:
        print "failed 4"

    b = SetBuilder()
    store.visit(o(b.accept), (None, None, None))

    b.filter(my_filter)
    
    if b.set == [literal("37")]:
        print "passed 5"
        passed = passed + 1
    else:
        print "failed 5: get", b.list




    if passed == 5:
        return (1, "ALL TESTED PASSED")
    elif passed > 1:
        return (0, "ONLY %s TESTS PASSED" % passed)
    elif passed == 1:
        return (0, "ONLY 1 TEST PASSED")
    else:
        return (0, "NO TESTS PASSED")





