# $Header$

# This is pylog, an attempt to implement Prolog-like inference in Python

test = 0

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
if test: print isFact((('man', 'socrates'),)), 1
# and isFact((("mortal","socrates"),("man","socrates"))) should return 0
if test: print isFact((("mortal","socrates"),("man","socrates"))), 0

# conditionals may include variables
# for example, "all men are mortals" could be expressed as
# ("mortal","_X"),("man","_X")
#
# variables begin with _
def isVariable(token):
    return token[0]=="_"

# so, isVariable("foo") should return 0
if test: print isVariable("foo"), 0
# and isVariable("_foo") should return 1
if test: print isVariable("_foo"), 1

# conditionals and facts are stored in a list called db
db = []

# adding a new fact or conditional just involves appending to the db list
def add(*conditional_or_fact):
    db.append(conditional_or_fact)

# so, add(("man","socrates")) adds "socrates is a man"
if test: add(("man","socrates"))
# and add(("mortal","_X"),("man","_X")) adds "all men are mortal"
if test: add(("mortal","_X"),("man","_X"))

# and the result is that db should equal:
# [(('man', 'socrates'),), (('mortal', '_X'), ('man', '_X'))]
if test: print db

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
if test: print match(("foo"),("bar")), 0
# so, match(("foo"),("foo")) should return 1
if test: print match(("foo"),("foo")), 1
# so, match(("foo","bar"),("foo","baz")) should return 0
if test: print match(("foo","bar"),("foo","baz")), 0
# so, match(("foo","bar"),("foo","bar")) should return 1
if test: print match(("foo","bar"),("foo","bar")), 1

# the may_match function returns the variable binding(s) that must be
#   true if the two given clauses are to match
# a return of None means a match is impossible
# a return of an empty dictionary means a match is possible regardless of
#   variable binding(s)
def may_match(clause1, clause2):
#    print "may_match", clause1, clause2
    binding = ({},{})
    if len(clause1)==len(clause2):
        for i in range(0,len(clause1)):
            if clause1[i]!=clause2[i]:
                if isVariable(clause1[i]):
                    if binding[0].has_key(clause1[i]) and binding[0][clause1[i]] != clause2[i]:
                        return None
                    else: 
                        binding[0][clause1[i]] = clause2[i]
                elif isVariable(clause2[i]):
                    if binding[1].has_key(clause2[i]) and binding[1][clause2[i]] != clause1[i]:
                        return None
                    else: 
                        binding[1][clause2[i]] = clause1[i]
                else:
                    return None
        return binding
    return None

test0 = 0
# so, may_match(("foo","bar"),("foo","baz")) should return None
if test0: print may_match(("foo","bar"),("foo","baz"))
# so, may_match(("foo","bar"),("foo","bar")) should return ({},{})
if test0: print may_match(("foo","bar"),("foo","bar"))
# so, may_match(("foo","_X"),("foo","bar")) should return ({'_X': 'bar'},{})
if test0: print may_match(("foo","_X"),("foo","bar"))
# so, may_match(("_X","_Y"),("foo","bar")) should return
#   ({'_X': 'foo', '_Y': 'bar'},{})
if test0: print may_match(("_X","_Y"),("foo","bar"))

# so, may_match(("_X","_X"),("foo","bar")) should return None
if test0: print may_match(("_X","_X"),("foo","bar"))
# so, may_match(("_X","_X"),("foo","foo")) should return ({'_X': 'foo'},{})
if test0: print may_match(("_X","_X"),("foo","foo"))

# so, may_match(("foo","foo"),("_X","_X")) should return ({},{'_X': 'foo'})
if test0: print may_match(("foo","foo"),("_X","_X"))

# the substitute function takes a clause containing variables and a dictionary
#   of bindings and performs variable substitution
def substitute(clause, bindings):
    l = []
    for item in clause:
        if isVariable(item) and bindings.has_key(item):
            l.append(bindings[item])
        else:
            l.append(item)
    return tuple(l)

# so substitute(("foo","_X"),{"_X":"bar"}) should return ('foo', 'bar')
if test0: print substitute(("foo","_X"),{"_X":"bar"}), "('foo', 'bar')"
# TODO handle exception of unknown variable

# the goal function is used to find out whether something is true or not
# at the moment, it can only take a single clause and it must not contain
# variables (but I'm working on variables now)
def goal(clause, binding={}):
    print
    print "testing to see if %s is true assuming %s" % (str(clause),binding)
    solutions = []
    for c in db:
        print "  checking against %s" % str(c),
        if isFact(c):
            print "which is a fact"
            b = may_match(c[0],substitute(clause,binding))
            if b != None:
                print "    a match, assuming", b
                solutions.append(b[1])
            else:
                #pass
                print "    no match"
        else:
            print "which is a conditional"
            b = may_match(c[0],clause)
            if b != None:
                print "    a match, assuming", b
                (lb,rb) = b
                for cond in c[1:]:
                    c = goal(cond, lb)
                    if c==[]:
                        print "  returning []"
                        return []
                    else:
                        pass
                        #solutions = solutions + c
                print "adding a solution", rb
                solutions.append(rb)
            else:
                pass
                print "    no match"
    print "  returning", solutions
    return solutions
# TODO conditional chaining will not work :-(

test1 = 0

if test1: add(("man","socrates"))
if test1: add(("mortal","_X"),("man","_X"))

# for example, goal(("man","socrates")) should return [{}]
if test1: print goal(("man","socrates")), "[{}]"
# and goal(("bird","socrates")) should return []
if test1: print goal(("bird","socrates")), "[]"

# and goal(("human","socrates")) should return [{}]
if test1: add(("human","socrates"),("man","socrates"))
if test1: print goal(("human","socrates")), "[{}]"

# and goal(("mortal","socrates")) should return [{}]
if test1: print goal(("mortal","socrates")), "[{}]"

test2 = 0

if test2: add(("man","socrates"))
if test2: add(("man","plato"))
if test2: print goal(("_X","socrates")),"[{'_X': 'man'}]"
if test2: print goal(("_X","plato")),"[{'_X': 'man'}]"
if test2: print goal(("man","_X")),"[{'_X': 'socrates'}, {'_X': 'plato'}]"
if test2: print goal(("bird","_X")),"[]"

if test2: add(("foo","bar","baz"))
if test2: print goal(("foo","_X","_Y")), "[{'_X': 'bar', '_Y': 'baz'}]"

test3 = 0

if test3: add(("foo","bar"))
if test3: add(("foo","foo"))
if test3: print goal(("_X","_Y"))
if test3: print goal(("_X","_X"))

test4 = 1

if test4: add(("fred","type","turtle"))
if test4: add(("_X","num-legs","4"),("_X","type","turtle"))
if test4: print goal(("fred","num-legs","_X"))

# $Log$
# Revision 7.0  2001/03/26 23:41:04  eikeon
# NEW RELEASE
#
# Revision 6.0  2001/02/19 05:01:23  jtauber
# new release
#
# Revision 5.0  2000/12/08 08:34:52  eikeon
# new release
#
# Revision 4.0  2000/11/06 15:57:33  eikeon
# VERSION 4.0
#
# Revision 1.4  2000/11/04 06:13:47  jtauber
# greatly improve capabilities of inference engine. in particular, goals can have variables
#
# Revision 1.3  2000/11/02 21:48:26  eikeon
# removed old log messages
#
# Revision 1.2  2000/10/31 06:30:28  eikeon
# removed ^M's
#
# Revision 1.1  2000/10/31 06:15:45  jtauber
# initial attempt at prolog-like inference in python
