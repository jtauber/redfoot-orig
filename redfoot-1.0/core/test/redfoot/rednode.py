from redfoot.rednode import RedNode
from redfoot.rdf.const import *

from redfoot.rdf.objects import resource, literal

from redfoot.rdf.query.functors import *

class TestResult:

    def __init__(self):
        self.classes = {}
        self.current_class = None
    
    def add_class(self, c):
        self.classes[str(c)] = {}
        self.current_class = str(c)

    def add_instance(self, i):
        self.classes[self.current_class][str(i)] = 1


class TestResult2:

    def __init__(self): 
        self.result = []

    def add_list(self, *args):
        self.result.append(map(str, args))
        return 1


def run():
    rednode = RedNode()

    rednode.local.add(resource("john"), resource("age"), literal("37"))
    rednode.local.add(resource("paul"), resource("age"), literal("35"))
    rednode.local.add(resource("peter"), resource("age"), literal("35"))
    rednode.local.add(resource("john"), TYPE, resource("person"))
    rednode.local.add(resource("peter"), TYPE, resource("fish"))
    
    rednode.local.add(resource("john"), LABEL, literal("John"))
    rednode.local.add(resource("paul"), LABEL, literal("Paul"))
    rednode.local.add(resource("peter"), LABEL, literal("Peter"))
    
    rednode.local.add(resource("john"), resource("knows"), resource("paul"))
    rednode.local.add(resource("paul"), resource("knows"), resource("peter"))
    rednode.local.add(resource("peter"), resource("knows"), resource("mark"))

    rednode.local.add(resource("design_patterns"), TYPE, resource("book"))

    rednode.local.add(resource("person"), TYPE, CLASS)
    rednode.local.add(resource("fish"), TYPE, CLASS)
    rednode.local.add(resource("book"), TYPE, CLASS)
    
    rednode.local.add(resource("animate"), TYPE, CLASS)
    rednode.local.add(resource("person"), SUBCLASSOF, resource("animate"))
    rednode.local.add(resource("person"), SUBCLASSOF, resource("some_superclass"))
    rednode.local.add(resource("fish"), SUBCLASSOF, resource("animate"))

    rednode.local.add(resource("age"), DOMAIN, resource("person"))
    rednode.local.add(resource("knows"), DOMAIN, resource("person"))
    rednode.local.add(resource("age"), RANGE, LITERAL)
    rednode.local.add(resource("knows"), RANGE, resource("animate"))

    rednode.local.add(resource("age"), TYPE, PROPERTY)
    rednode.local.add(resource("knows"), TYPE, PROPERTY)

    passed = 0
    
    t = TestResult()
    rednode.visit_resources_by_type(t.add_class, t.add_instance)
    correct = {'http://www.w3.org/2000/01/rdf-schema#Class': {'http://www.w3.org/2000/01/rdf-schema#Class': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Alt': 1, 'http://www.w3.org/2000/01/rdf-schema#Resource': 1, 'http://www.w3.org/2000/01/rdf-schema#ConstraintProperty': 1, 'animate': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq': 1, 'http://www.w3.org/2000/01/rdf-schema#Literal': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#UIType': 1, 'http://www.w3.org/2000/01/rdf-schema#ConstraintResource': 1, 'person': 1, 'http://www.w3.org/2000/01/rdf-schema#ContainerMembershipProperty': 1, 'fish': 1, 'book': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement': 1, 'http://www.w3.org/2000/01/rdf-schema#Container': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#YesNo': 1}, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property': {'http://www.w3.org/2000/01/rdf-schema#label': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#uiType': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#value': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate': 1, 'http://www.w3.org/2000/01/rdf-schema#subClassOf': 1, 'http://www.w3.org/2000/01/rdf-schema#isDefinedBy': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#subject': 1, 'http://www.w3.org/2000/01/rdf-schema#subPropertyOf': 1, 'age': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#object': 1, 'http://www.w3.org/2000/01/rdf-schema#comment': 1, 'knows': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#requiredProperty': 1, 'http://www.w3.org/2000/01/rdf-schema#seeAlso': 1}, 'fish': {'peter': 1}, 'http://www.w3.org/2000/01/rdf-schema#ConstraintProperty': {'http://www.w3.org/2000/01/rdf-schema#domain': 1, 'http://www.w3.org/2000/01/rdf-schema#range': 1}, 'http://www.w3.org/TR/WD-rdf-schema#Class': {'http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Alt': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag': 1}, 'book': {'design_patterns': 1}, 'http://redfoot.sourceforge.net/2000/10/06/builtin#UIType': {'http://redfoot.sourceforge.net/2000/10/06/builtin#TEXTAREA': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#TEXTINPUT': 1}, 'http://redfoot.sourceforge.net/2000/10/06/builtin#YesNo': {'http://redfoot.sourceforge.net/2000/10/06/builtin#NO': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#YES': 1}, 'person': {'john': 1}}
    if t.classes == correct:
        passed = passed + 1
    else:
        print "TEST 1 FAILED", t.classes
        
    t = TestResult()
    rednode.local.visit_resources_by_type(t.add_class, t.add_instance)
    correct = {'http://www.w3.org/2000/01/rdf-schema#Class': {'fish': 1, 'book': 1, 'animate': 1, 'person': 1}, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property': {'age': 1, 'knows': 1}, 'book': {'design_patterns': 1}, 'fish': {'peter': 1}, 'person': {'john': 1}}
    if t.classes == correct:
        passed = passed + 1
    else:
        print "TEST 2 FAILED", t.classes

    t = TestResult()
    rednode.neighbours.visit_resources_by_type(t.add_class, t.add_instance)
    correct = {'http://www.w3.org/2000/01/rdf-schema#ConstraintProperty': {'http://www.w3.org/2000/01/rdf-schema#domain': 1, 'http://www.w3.org/2000/01/rdf-schema#range': 1}, 'http://www.w3.org/2000/01/rdf-schema#Class': {'http://www.w3.org/2000/01/rdf-schema#Class': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Alt': 1, 'http://www.w3.org/2000/01/rdf-schema#Resource': 1, 'http://www.w3.org/2000/01/rdf-schema#ConstraintProperty': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq': 1, 'http://www.w3.org/2000/01/rdf-schema#Literal': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#UIType': 1, 'http://www.w3.org/2000/01/rdf-schema#ConstraintResource': 1, 'http://www.w3.org/2000/01/rdf-schema#ContainerMembershipProperty': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement': 1, 'http://www.w3.org/2000/01/rdf-schema#Container': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#YesNo': 1}, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property': {'http://www.w3.org/2000/01/rdf-schema#label': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#uiType': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#value': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate': 1, 'http://www.w3.org/2000/01/rdf-schema#subClassOf': 1, 'http://www.w3.org/2000/01/rdf-schema#isDefinedBy': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#subject': 1, 'http://www.w3.org/2000/01/rdf-schema#subPropertyOf': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#object': 1, 'http://www.w3.org/2000/01/rdf-schema#comment': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#requiredProperty': 1, 'http://www.w3.org/2000/01/rdf-schema#seeAlso': 1}, 'http://www.w3.org/TR/WD-rdf-schema#Class': {'http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Alt': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag': 1}, 'http://redfoot.sourceforge.net/2000/10/06/builtin#UIType': {'http://redfoot.sourceforge.net/2000/10/06/builtin#TEXTAREA': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#TEXTINPUT': 1}, 'http://redfoot.sourceforge.net/2000/10/06/builtin#YesNo': {'http://redfoot.sourceforge.net/2000/10/06/builtin#NO': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#YES': 1}}
    if t.classes == correct:
        passed = passed + 1
    else:
        print "TEST 3 FAILED", t.classes
    
    t = TestResult()
    rednode.neighbourhood.visit_resources_by_type(t.add_class, t.add_instance)
    correct = {'http://www.w3.org/2000/01/rdf-schema#Class': {'http://www.w3.org/2000/01/rdf-schema#Class': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Alt': 1, 'http://www.w3.org/2000/01/rdf-schema#Resource': 1, 'http://www.w3.org/2000/01/rdf-schema#ConstraintProperty': 1, 'animate': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq': 1, 'http://www.w3.org/2000/01/rdf-schema#Literal': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#UIType': 1, 'http://www.w3.org/2000/01/rdf-schema#ConstraintResource': 1, 'person': 1, 'http://www.w3.org/2000/01/rdf-schema#ContainerMembershipProperty': 1, 'fish': 1, 'book': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement': 1, 'http://www.w3.org/2000/01/rdf-schema#Container': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#YesNo': 1}, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property': {'http://www.w3.org/2000/01/rdf-schema#label': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#uiType': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#value': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate': 1, 'http://www.w3.org/2000/01/rdf-schema#subClassOf': 1, 'http://www.w3.org/2000/01/rdf-schema#isDefinedBy': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#subject': 1, 'http://www.w3.org/2000/01/rdf-schema#subPropertyOf': 1, 'age': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#object': 1, 'http://www.w3.org/2000/01/rdf-schema#comment': 1, 'knows': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#requiredProperty': 1, 'http://www.w3.org/2000/01/rdf-schema#seeAlso': 1}, 'fish': {'peter': 1}, 'http://www.w3.org/2000/01/rdf-schema#ConstraintProperty': {'http://www.w3.org/2000/01/rdf-schema#domain': 1, 'http://www.w3.org/2000/01/rdf-schema#range': 1}, 'http://www.w3.org/TR/WD-rdf-schema#Class': {'http://www.w3.org/1999/02/22-rdf-syntax-ns#Seq': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Alt': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement': 1, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag': 1}, 'book': {'design_patterns': 1}, 'http://redfoot.sourceforge.net/2000/10/06/builtin#UIType': {'http://redfoot.sourceforge.net/2000/10/06/builtin#TEXTAREA': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#TEXTINPUT': 1}, 'http://redfoot.sourceforge.net/2000/10/06/builtin#YesNo': {'http://redfoot.sourceforge.net/2000/10/06/builtin#NO': 1, 'http://redfoot.sourceforge.net/2000/10/06/builtin#YES': 1}, 'person': {'john': 1}}
    if t.classes == correct:
        passed = passed + 1
    else:
        print "TEST 4 FAILED", t.classes

    t = TestResult2()
    val = rednode.visit(t.add_list, (None, None, None))

    if val==1 and len(t.result)==1:
        passed = passed + 1
    else:
        print "TEST 4 FAILED", val, len(t.result)


    if passed == 5:
        return (1, "ALL TESTS PASSED")
    elif passed > 1:
        return (0, "ONLY %s TESTS PASSED" % passed)
    elif passed == 1:
        return (0, "ONLY 1 TEST PASSED")
    else:
        return (0, "ALL TESTS FAILED")







