import pyexpat

from rdf.store import *
from rdf.storeio import *
from rdf.query import *

from rdf.const import *

from redfoot.rednode import RedNode 


store = RedNode()

print store.get(CLASS, TYPE, None)
print store.label(CLASS)
print store.comment(CLASS)

store.local.add("vehicle", TYPE, CLASS)
store.local.add("vehicle", SUBCLASSOF, RESOURCE)
store.local.add("car", TYPE, CLASS)
store.local.add("car", SUBCLASSOF, "vehicle")
store.local.add("two-door-car", TYPE, CLASS)
store.local.add("two-door-car", SUBCLASSOF, "car")
store.local.add("my-car", TYPE, "car")
store.local.add("my-car", LABEL, "^My Car")

store.local.add("color", TYPE, PROPERTY)
store.local.add("color", DOMAIN, "car")
store.local.add("color", RANGE, LITERAL)

store.local.add("cooler_than", TYPE, PROPERTY)
store.local.add("cooler_than", DOMAIN, "car")
#store.local.add("cooler_than", RANGE, "car")
store.local.add("cooler_than", RANGE, "vehicle")



print store.getByType("car", None, None)
print store.getByType("car", LABEL, "^My Car")

print store.isOfType("my-car", "car")
print store.isOfType("my-car", "vehicle")
print store.isOfType("my-car", "giraffe")

store.local.add("car", SUBCLASSOF, "fast-things")

#print store.typeInh("car")

#print store.transitiveSuperTypes("car")

#print store.transitiveSubTypes("vehicle")
class StatementSetBuilder:
    def __init__(self):
        self.set = {}

    def visit(self, s, p, o):
        self.set[(s, p, o)] = 1

    def flush(self):
        pass
    
visitor = StatementSetBuilder()
store.visitTransitiveSubTypes(visitor, "vehicle")
print "Transitive Sub Types of vehicle: %s" % visitor.set
print "Transitive Sub Types of vehicle: %s" % store.getTransitiveSubTypes("vehicle")
print "Transitive super Types of car: %s" % store.getTransitiveSuperTypes("two-door-car")

visitor = StatementSetBuilder()
store.visitPossibleValues(visitor.visit, "cooler_than")
print "Possible values for property cooler_than: %s" % visitor.set

visitor = StatementSetBuilder()
store.visitPossiblePropertiesForSubject(visitor.visit, "my-car")
print "Possible properties for my_car: %s" % visitor.set



#def cDisplay(c,indent=0):
#    print indent*"  ","-", c

#def rDisplay(r,indent=0):
#    print indent*"  ","  *",r

#print store.resourcesByClassV(cDisplay, rDisplay)

#print "root classes: ", store.rootClasses()

#print 79*"-"
#print store.subClassV(RESOURCE, cDisplay, rDisplay)

#print 79*"-"
#print store.getPossibleValues(RANGE)

#          def pv(s, p, o, response=response):
#              response.write("""
#              <li>%s</li>           
#          """ % s)
#          self.storeNode.visitPossibleValues(pv, "http://xteam.hq.bowstreet.com/2000/10/#subject")

