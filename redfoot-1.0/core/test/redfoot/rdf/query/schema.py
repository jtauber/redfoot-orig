from redfoot.rdf.store import triple
from redfoot.rdf.objects import resource, literal

from redfoot.rdf.query.schema import *

from redfoot.rdf.const import *

def compare_lists(list1, list2):
    for item in list1:
        if not item in list2:
            return 0
    for item in list2:
        if not item in list1:
            return 0
    return 1

class QueryStore(SchemaQuery, triple.TripleStore):
    pass

def run():

    passed = 0

    store = QueryStore()

    store.add(resource("john"), resource("age"), literal("37"))
    store.add(resource("paul"), resource("age"), literal("35"))
    store.add(resource("peter"), resource("age"), literal("35"))
    store.add(resource("john"), TYPE, resource("person"))
    store.add(resource("peter"), TYPE, resource("fish"))

    store.add(resource("john"), LABEL, literal("John"))
    store.add(resource("paul"), LABEL, literal("Paul"))
    store.add(resource("peter"), LABEL, literal("Peter"))

    store.add(resource("john"), resource("knows"), resource("paul"))
    store.add(resource("paul"), resource("knows"), resource("peter"))
    store.add(resource("peter"), resource("knows"), resource("mark"))

    store.add(resource("design_patterns"), TYPE, resource("book"))

    store.add(resource("person"), TYPE, CLASS)
    store.add(resource("fish"), TYPE, CLASS)
    store.add(resource("book"), TYPE, CLASS)

    store.add(resource("animate"), TYPE, CLASS)
    store.add(resource("person"), SUBCLASSOF, resource("animate"))
    store.add(resource("person"), SUBCLASSOF, resource("some_superclass"))
    store.add(resource("fish"), SUBCLASSOF, resource("animate"))

    store.add(resource("age"), DOMAIN, resource("person"))
    store.add(resource("knows"), DOMAIN, resource("person"))
    store.add(resource("age"), RANGE, LITERAL)
    store.add(resource("knows"), RANGE, resource("animate"))

    if store.is_of_type(resource("john"), resource("person")):
        print "passed 1"
        passed = passed + 1
    else:
        print "failed 1"
        
    if not store.is_of_type(resource("peter"), resource("person")):
        print "passed 2"
        passed = passed + 1
    else:
        print "failed 2"

    if not store.is_of_type(resource("fred"), resource("person")):
        print "passed 3"
        passed = passed + 1
    else:
        print "failed 3"

    class TestResult:
        def __init__(self):
            self.result = []

        def add_list(self, *args):
            self.result.append(map(str, args))

    t = TestResult()
    store.visit_typeless_resources(t.add_list)
    correct = [['age'], ['paul'], ['knows']]
    if compare_lists(t.result, correct):
        print "passed 4"
        passed = passed + 1
    else:
        print "failed 4"

    t = TestResult()
    store.visit_by_type(t.add_list, resource("person"), resource("age"), literal("35"))
    if t.result == []:
        print "passed 5"
        passed = passed + 1
    else:
        print "failed 5"

    t = TestResult()
    store.visit_by_type(t.add_list, resource("person"), resource("age"), literal("37"))
    correct = [['john', 'age', '37']]
    if compare_lists(t.result, correct):
        print "passed 6"
        passed = passed + 1
    else:
        print "failed 6"

    if str(store.label(resource("john"))) == "John":
        print "passed 7"
        passed = passed + 1
    else:
        print "failed 7"

    t = TestResult()
    store.visit_transitive(t.add_list, resource("john"), resource("knows"))
    correct = [['john', 'knows', 'paul'], ['paul', 'knows', 'peter'], ['peter', 'knows', 'mark']]
    if compare_lists(t.result, correct):
        print "passed 8"
        passed = passed + 1
    else:
        print "failed 8"
    
    t = TestResult()
    store.visit_transitive_reverse(t.add_list, resource("mark"), resource("knows"))
    correct = [['peter', 'knows', 'mark'], ['paul', 'knows', 'peter'], ['john', 'knows', 'paul']]
    if compare_lists(t.result, correct):
        print "passed 9"
        passed = passed + 1
    else:
        print "failed 9"

    if store.exists(resource("person"), SUBCLASSOF, resource("animate")):
        print "passed 10"
        passed = passed + 1
    else:
        print "failed 10"

    if not store.exists(resource("book"), SUBCLASSOF, resource("animate")):
        print "passed 11"
        passed = passed + 1
    else:
        print "failed 11"

    if store.exists(resource("person"), SUBCLASSOF, None):
        print "passed 12"
        passed = passed + 1
    else:
        print "failed 12"

    if not store.exists(resource("book"), SUBCLASSOF, None):
        print "passed 13"
        passed = passed + 1
    else:
        print "failed 13"

    t = TestResult()
    store.visit_root_classes(s(t.add_list))
    correct = [['animate'], ['book']]
    if compare_lists(t.result, correct):
        print "passed 14"
        passed = passed + 1
    else:
        print "failed 14"

    t = TestResult()
    store.visit_parent_types(o(t.add_list), resource("person"))
    correct = [['some_superclass'], ['animate']]
    if compare_lists(t.result, correct):
        print "passed 15"
        passed = passed + 1
    else:
        print "failed 15"

    t = TestResult()
    store.visit_possible_properties(t.add_list, resource("person"))
    correct = [['knows'], ['age']]
    if compare_lists(t.result, correct):
        print "passed 16"
        passed = passed + 1
    else:
        print "failed 16"

    t = TestResult()
    store.visit_possible_properties_for_subject(t.add_list, resource("john"))
    correct = [['knows'], ['age']]
    if compare_lists(t.result, correct):
        print "passed 17"
        passed = passed + 1
    else:
        print "failed 17"

    t = TestResult()
    store.visit_ranges(t.add_list, resource("age"))
    correct = [['http://www.w3.org/2000/01/rdf-schema#Literal']]
    if compare_lists(t.result, correct):
        print "passed 18"
        passed = passed + 1
    else:
        print "failed 18"

    t = TestResult()
    store.visit_ranges(t.add_list, resource("knows"))
    correct = [['animate']]
    if compare_lists(t.result, correct):
        print "passed 19"
        passed = passed + 1
    else:
        print "failed 19"
    
    t = TestResult()
    store.visit_possible_values(t.add_list, resource("knows"))
    correct = [['peter'], ['john']]
    if compare_lists(t.result, correct):
        print "passed 20"
        passed = passed + 1
    else:
        print "failed 20"
    
    class TestResult2:

        def __init__(self):
            self.classes = {}
            self.current_class = None

        def add_class(self, c):
            self.classes[str(c)] = {}
            self.current_class = str(c)

        def add_instance(self, i):
            self.classes[self.current_class][str(i)] = 1


    t = TestResult2()
    store.visit_resources_by_type(t.add_class, t.add_instance)
    correct = {'http://www.w3.org/2000/01/rdf-schema#Class': {'fish': 1, 'book': 1, 'animate': 1, 'person': 1}, 'book': {'design_patterns': 1}, 'fish': {'peter': 1}, 'person': {'john': 1}}
    if t.classes == correct:
        print "passed 21"
        passed = passed + 1
    else:
        print "failed 21"

    class TestResult3:

        def __init__(self):
            self.classes = {}
            self.current_class = None

        def add_class(self, c, depth):
            self.classes[str(c) + str(depth)] = {}
            self.current_class = str(c) + str(depth)

        def add_instance(self, i, depth):
            self.classes[self.current_class][str(i) + str(depth)] = 1

    def nop(*args):
        pass

    t = TestResult3()
    store.visit_subclasses(t.add_class, nop, t.add_instance, resource("animate"), 1)
    correct = {'animate0': {}, 'fish1': {'peter1': 1}, 'person1': {'john1': 1}}
    if t.classes == correct:
        print "passed 22"
        passed = passed + 1
    else:
        print "failed 22"

    t = TestResult3()
    store.visit_subclasses(t.add_class, nop, t.add_instance, resource("animate"), 0)
    correct = {'animate0': {}, 'fish1': {}, 'person1': {}}
    if t.classes == correct:
        print "passed 23"
        passed = passed + 1
    else:
        print "failed 23"

    if passed == 23:
        return (1, "ALL TESTS PASSED")
    elif passed > 1:
        return (0, "ONLY %s TESTS PASSED" % passed)
    elif passed == 1:
        return (0, "ONLY 1 TEST PASSED")
    else:
        return (0, "ALL TESTS FAILED")
