# $Header$

# This is pylog, an attempt to implement Prolog-like inference in Python

# a _clause_ is expressed as a tuple
# for example, "socrates is a man" could be expressed as
# ("man","socrates")

# a _conditional_ is a sequence of clauses
# the first clause is only true if all subsequent clauses are true
# for example, "socrates is mortal if socrates is a man" could be expressed as
# ("mortal","socrates"),("man","socrates")

# a conditional with only one clause is called a _fact_
# for example,
# ("man","socrates")
# is a fact

def isFact(c):
    return len(c)==1

# so isFact((('man', 'socrates'),)) should return 1
print isFact((('man', 'socrates'),))
# and isFact((("mortal","socrates"),("man","socrates"))) should return 0
print isFact((("mortal","socrates"),("man","socrates")))

# conditionals may include variables
# for example, "all men are mortals" could be expressed as
# ("mortal","_X"),("man","_X")
#
# variables begin with _
def isVariable(token):
    return token[0]=="_"

# so, isVariable("foo") should return 0
print isVariable("foo")
# and isVariable("_foo") should return 1
print isVariable("_foo")

# conditionals and facts are stored in a list called db
db = []

# adding a new fact or conditional just involves appending to the db list
def add(*conditional_or_fact):
    db.append(conditional_or_fact)

# so, add(("man","socrates")) adds "socrates is a man"
add(("man","socrates"))
# and add(("mortal","_X"),("man","_X")) adds "all men are mortal"
add(("mortal","_X"),("man","_X"))

# and the result is that db should equal:
# [(('man', 'socrates'),), (('mortal', '_X'), ('man', '_X'))]
print db

# the match function is used to determine whether two clauses match
# this will only be the case if each item of the tuple is equal
def match(clause1, clause2):
    if len(clause1)==len(clause2):
        for i in range(0,len(clause1)):
            if clause1[i]!=clause2[i]:
                return 0
        return 1
    return 0

# so, match(("foo"),("bar")) should return 0
print match(("foo"),("bar"))
# so, match(("foo"),("foo")) should return 1
print match(("foo"),("foo"))
# so, match(("foo","bar"),("foo","baz")) should return 0
print match(("foo","bar"),("foo","baz"))
# so, match(("foo","bar"),("foo","bar")) should return 1
print match(("foo","bar"),("foo","bar"))

# the may_match function returns the variable binding(s) that must be
#   true if the two given clauses are to match
# a return of None means a match is impossible
# a return of an empty dictionary means a match is possible regardless of
#   variable binding(s)
# at present the second clause may not contain variables
def may_match(clause1, clause2):
    binding = {}
    if len(clause1)==len(clause2):
        for i in range(0,len(clause1)):
            if clause1[i]!=clause2[i]:
                if isVariable(clause1[i]):
                    binding[clause1[i]] = clause2[i]
                else:
                    return None
        return binding
    return None

# so, may_match(("foo","bar"),("foo","baz")) should return None
print may_match(("foo","bar"),("foo","baz"))
# so, may_match(("foo","bar"),("foo","bar")) should return {}
print may_match(("foo","bar"),("foo","bar"))
# so, may_match(("foo","_X"),("foo","bar")) should return {'_X': 'bar'}
print may_match(("foo","_X"),("foo","bar"))
# so, may_match(("_X","_Y"),("foo","bar")) should return
#   {'_X': 'foo', '_Y': 'bar'}
print may_match(("_X","_Y"),("foo","bar"))

# the substitute function takes a clause containing variables and a dictionary
#   of bindings and performs variable substitution
def substitute(clause, bindings):
    l = []
    for item in clause:
        if isVariable(item):
            l.append(bindings[item])
        else:
            l.append(item)
    return tuple(l)

# so substitute(("foo","_X"),{"_X":"bar"}) should return ("foo","bar")
print substitute(("foo","_X"),{"_X":"bar"})
# TODO handle exception of unknown variable

# the goal function is used to find out whether something is true or not
# at the moment, it can only take a single clause and it must not contain
# variables
def goal(clause, binding={}):
    #print "testing to see if %s is true with binding %s" % (str(clause),binding)
    for c in db:
        #print "checking against %s" % str(c),
        if isFact(c):
            #print "which is a fact"
            if match(c[0],substitute(clause,binding)):
                #print "match"
                return 1
            else:
                pass
                #print "no match"
        else:
            #print "which is a conditional"
            b = may_match(c[0],clause)
            #print "binding = ", b
            if b != None:
                for cond in c[1:]:
                    if not goal(cond, b):
                        return 0
                return 1
    return 0
# TODO conditional chaining will not work :-(

# for example, goal(("man","socrates")) should return 1
print goal(("man","socrates"))
# and goal(("bird","socrates")) should return 0
print goal(("bird","socrates"))

# and goal(("human","socrates")) should return 1
add(("human","socrates"),("man","socrates"))
print goal(("human","socrates"))

# and goal(("mortal","socrates")) should return 1
print goal(("mortal","socrates"))

# $Log$


