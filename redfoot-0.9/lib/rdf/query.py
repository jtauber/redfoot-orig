# $Header$
from rdf.literal import literal, un_literal, is_literal
from rdf.const import *

_s_ = lambda s, p, o: [s,]
_o_ = lambda s, p, o: [o,]

class QueryBase:

    def query(self, visitor, subject=None, predicate=None, object=None):
        self.visit(visitor.visit, subject, predicate, object)
        visitor.flush()
        
    def get(self, subject=None, predicate=None, object=None):
        listBuilder = ListBuilder()
        self.query(listBuilder, subject, predicate, object)
	return listBuilder.list

    def getFirst(self, subject, predicate, object):
        listBuilder = ListBuilder()
        self.query(First(listBuilder), subject, predicate, object)
        list = listBuilder.list
        if len(list)>0:
            return list[0]
        else:
            return None

    def isKnownResource(self, resource):
        """is the given resource known?"""
        if self.getFirst(resource, None, None)!=None:
            return 1
        else:
            return 0
        
    # TODO: should we have a version of this that answers for subclasses too?
    def isOfType(self, resource, type):
        """is the given resource of the given type"""
        statement = self.getFirst(resource, TYPE, type)
        if statement != None:
            return 1
        else:
            return 0

    def getTypelessResources(self):
        """returns those resources that don't have a type"""
        result = []
        def callback(s, p, o, result=result, self=self):
            if self.getFirst(s, TYPE, None)==None:
                result.append(s)
        self.visit(callback, None, None, None)

#        query = Query(
#        self.query(
        return result

    def visitTypelessResources(self, callback):
        """returns those resources that don't have a type"""
        def adaptor(s, callback=callback, self=self):
            if self.getFirst(s, TYPE, None)==None:
                callback(s)
        self.visit_subjects(adaptor)

    # TODO: need a visitor version
    def getByType(self, type, predicate, object):
        listBuilder = ListBuilder()
        query = Query(self.query, (listBuilder, _s_, predicate, object))
        self.query(query, None, TYPE, type)
        return listBuilder.list

    def visitByType(self, visitor, type, predicate, object):
        query = Query(self.query, (visitor, _s_, predicate, object))
        self.query(query, None, TYPE, type)

    def visitResourcesByType(self, processClass, processResource):
        setBuilder = ObjectSetBuilder()
        self.query(setBuilder, None, TYPE, None)
        types = setBuilder.set.keys()
        for klass in types:
            if self.getFirst(None, TYPE, klass)!=None:
                processClass(klass)
                query = Query(processResource, (_s_,))
                self.query(query, None, TYPE, klass)

    def visitPredicateObjectPairsForSubject(self, predicateObject_callback, subject):
        query = Query(predicateObject_callback, (lambda s, p, o: [p, o],))
        self.query(query, subject, None, None)

    # REIFICATION STUFF

    def visitReifiedStatementsAboutSubject(self, callback, subject):
        def adapter(callback, subject, getFirst):
            callback(subject, getFirst(subject, PREDICATE, None)[2], getFirst(subject, OBJECT, None)[2])

        visitor = Query(adapter, (callback, _s_, self.getFirst))
        self.visitByType(visitor, STATEMENT, SUBJECT, subject)

    # should perhaps just autogenerate statement_uri
    def reify(self, statement_uri, subject, predicate, object):
        self.local.add(statement_uri, TYPE, STATEMENT)
        self.local.add(statement_uri, SUBJECT, subject)
        self.local.add(statement_uri, PREDICATE, predicate)
        self.local.add(statement_uri, OBJECT, object)

    # TODO: not sure this makes sense to have - jkt
    def dereify(self, statement_uri):
        subject = self.get(statement, SUBJECT, None)[0][2]
        predicate = self.get(statement, PREDICATE, None)[0][2]
        object = self.get(statement, OBJECT, None)[0][2]
        self.local.add(subject, predicate, object)
        #self.removeAll(statement)


class First:
    def __init__(self, visitor=None):
        self.visitor = visitor
    
    def visit(self, s, p, o):
        if self.visitor:
            return self.visitor.visit(s, p, o)
        return 1 # tell visitor to stop

    def flush(self):
        pass
    
class Statement:
    def __init__(self):
        self.statement = None

    def visit(self, s, p, o):
        self.statement = (s, p, o)

    def flush(self):
        pass

    def object(self):
        if self.statement:
            return self.statement[2]
        else:
            return None
        
class ListBuilder:
    def __init__(self):
        self.list = []

    def visit(self, s, p, o):
        self.list.append((s, p, o))

    def flush(self):
        pass


class SubjectSetBuilder:
    def __init__(self):
        self.set = {}

    def visit(self, s, p, o):
        self.set[s] = 1

    def flush(self):
        pass

class ObjectSetBuilder:
    def __init__(self):
        self.set = {}

    def visit(self, s, p, o):
        self.set[o] = 1

    def flush(self):
        pass

class Query:
    def __init__(self, query, args):
        self.query = query
        self.pre = []
        self.post = []
        self.adapter = None
        for arg in args:
            if hasattr(arg, 'func_name'): # is arg a function
                self.adapter = arg
            else:
                if self.adapter == None:
                    self.pre.append(arg)
                else:
                    self.post.append(arg)

    def visit(self, s, p, o):
        return apply(self.query, self.pre + self.adapter(s, p, o) + self.post)

    def flush(self):
        if hasattr(self.query, 'flush'):
            self.query.flush()

class And:
    def __init__(self, first, second): 
        self.first = first 
        self.second = second 

    def visit(self, s, p, o):
        self.first.visit(s, p, o)
        self.second.visit(s, p, o)

    def flush(self):
        pass

class If:
    def __init__(self, first, second): 
        self.first = first 
        self.second = second 

    def visit(self, s, p, o):
        if self.first.visit(s, p, o)==None:
            return self.second.visit(s, p, o)
        else:
            return 1 # stop

    def flush(self):
        pass

class Alpha:
    def __init__(self, query, args, label):
        self.query = query
        self.statements = {}
        self.label = label
        self.pre = []
        self.post = []
        self.adapter = None
        for arg in args:
            if hasattr(arg, 'func_name'): # is arg a function
                self.adapter = arg
            else:
                if self.adapter == None:
                    self.pre.append(arg)
                else:
                    self.post.append(arg)

    def visit(self, s, p, o):
        label = self.label(s, '')
        self.statements[label+s] = (s, p, o)

    def flush(self):
        keys = self.statements.keys()
        keys.sort()
        for k in keys:
            s, p, o = self.statements[k]
            apply(self.query, self.pre + self.adapter(s, p, o) + self.post)


class QueryStore(QueryBase):

    # TODO: method to return all labels
    def label(self, subject, default=None):
        statement = Statement()
        self.query(First(statement), subject, LABEL, None)
        if statement.object():
            return un_literal(statement.object())
        elif default!=None:
            return default
        else:
            return subject

    def comment(self, subject, default=None):
        statement = self.getFirst(subject, COMMENT, None)
        if statement!=None:
            return un_literal(statement[2])
        elif default!=None:
            return default
        else:
            return self.label(subject)

    def getTransitiveSuperTypes(self, type):
        objectSetBuilder = ObjectSetBuilder()
        objectSetBuilder.set[type] = 1
        self.visitTransitiveSuperTypes(objectSetBuilder, type)
        return objectSetBuilder.set.keys()

    def visitTransitiveSuperTypes(self, callback, type):
        trans = And(callback, Query(self.visitTransitiveSuperTypes, (callback, _o_)))
        self.query(trans, type, SUBCLASSOF, None)

    def getTransitiveSubTypes(self, type):
        subjectSetBuilder = SubjectSetBuilder()
        subjectSetBuilder.set[type] = 1
        self.visitTransitiveSubTypes(subjectSetBuilder, type)
        return subjectSetBuilder.set.keys()

    def visitTransitiveSubTypes(self, callback, type):
        trans = And(callback, Query(self.visitTransitiveSubTypes, (callback, _s_)))
        self.query(trans, None, SUBCLASSOF, type)

    def getRootClasses(self):
        """returns those classes that aren't a subclass of anything"""
        # TODO: (1) use this in subclass view; (2) return unknown classes that appear as types
        result = []
        def klass(s, p, o, result=result, self=self):
            if self.getFirst(s, SUBCLASSOF, None)==None:
                result.append(s)
        self.visit(klass, None, TYPE, CLASS)
        return result

    def visitParentTypes(self, callback, type):
        query = Query(callback, (_o_,))                                 
        self.query(query, type, SUBCLASSOF, None)

    def visitSubclasses(self, class_callback, instance_callback, type, currentDepth=0, recurse=1):
        class_callback(type, currentDepth, recurse)

        if recurse:
            query = Query(self.visitSubclasses, (class_callback, instance_callback, _s_, currentDepth+1))
        else:
            query = Query(class_callback, (_s_, currentDepth+1, 0))
        self.query(query, None, SUBCLASSOF, type)
        
        instanceQuery = Query(instance_callback, (_s_, currentDepth, recurse))
        self.query(instanceQuery, None, TYPE, type)

    def getPossibleValues(self, property):
        resultset = {}

        def possibleSubject(subject, property, value, resultset=resultset):
            resultset[subject] = 1

        self.getPossibleValuesV(property, possibleSubject)

        return resultset.keys()
        
    # callback may be called more than once for the same possibleValue... user
    # of this method will have to remove duplicates
    def visitPossibleValues(self, callback, property):        
        ranges = self.get(property, RANGE, None)
        for range in ranges:
            for type in self.getTransitiveSubTypes(range[2]):
                self.visit(callback, None, TYPE, type)
            

    def visitPossibleProperties(self, callback, type):
        for superType in self.getTransitiveSuperTypes(type):
            self.visit(callback, None, DOMAIN, superType)

    # TODO rename "type" function
    def visitPossiblePropertiesForSubject(self, callback, subject):
        def adapter(s, p, o, self=self, callback=callback):
            self.visitPossibleProperties(callback, o)
        self.visit(adapter, subject, TYPE, None)
        # all subjects can take the properties that resource can
        # note: this will definitely lead to duplicates, but they are
        # possible anyway
        self.visitPossibleProperties(callback, RESOURCE)

    # TODO properties should be able to have more than one range
    def getRange(self, property):
        statement = self.getFirst(property, RANGE, None)
        if statement!=None:
            return statement[2]
        else:
            return None

#~ $Log$
#~ Revision 8.0  2001/04/27 00:52:13  eikeon
#~ new release
