# $Header$
from rdf.literal import literal, un_literal, is_literal
from rdf.const import *

class QueryStore:
    # TODO: method to return all labels

    def comment(self, subject, default=None):
        statement = self.getFirst(subject, COMMENT, None)
        if statement!=None:
            return un_literal(statement[2])
        elif default!=None:
            return default
        else:
            return self.label(subject)

    def isKnownResource(self, resource):
        if self.getFirst(resource, None, None)!=None:
            return 1
        else:
            return 0
        
    # TODO: should we have a version of this that answers for subclasses too?
    def isOfType(self, resource, type):
        statement = self.getFirst(resource, TYPE, type)
        if statement != None:
            return 1
        else:
            return 0

    def transitiveSuperTypes(self, type):
        objectSetBuilder = ObjectSetBuilder()
        objectSetBuilder.set[type] = 1
        query = Query(self.query, (objectSetBuilder,), lambda s, p, o: (o, SUBCLASSOF, None))
        self.superTypeV(query, type)
        return objectSetBuilder.set.keys()

    def superTypeV(self, visitor, type):
        self.query(visitor, type, SUBCLASSOF, None)

    def transitiveSubTypes(self, type):
        subjectSetBuilder = SubjectSetBuilder()
        subjectSetBuilder.set[type] = 1
        query = Query(self.query, (subjectSetBuilder,), lambda s, p, o: (None, SUBCLASSOF, s))
        self.subTypeV(query, type)
        return subjectSetBuilder.set.keys()

    def subTypeV(self, visitor, type):
        self.query(visitor, None, SUBCLASSOF, type)

    def rootClasses(self):
        """returns those classes that aren't a subclass of anything"""
        result = []
        def klass(s, p, o, result=result, self=self):
            if self.getFirst(s, SUBCLASSOF, None)==None:
                result.append(s)
        self.visit(klass, None, TYPE, CLASS)
        return result

    def typelessResources(self):
        """returns those resources that don't have a type"""
        result = []
        def callback(s, p, o, result=result, self=self):
            if self.getFirst(s, TYPE, None)==None:
                result.append(s)
        self.visit(callback, None, None, None)
        return result

    def typelessResourcesV(self, callback):
        """returns those resources that don't have a type"""
        def adaptor(s, callback=callback, self=self):
            if self.getFirst(s, TYPE, None)==None:
                callback(s)
        self.visitSubjects(adaptor)

    # visitor pattern
    def resourcesByClassV(self, processClass, processResource):
        processResourceV = Query(processResource, (), lambda s, p, o: (s,))
        queryV = Query(self.query, (processResourceV,), lambda s, p, o: (None, TYPE, s))

        processClassV = Query(processClass, (), lambda s, p, o: (s,))

        first = Query(self.query, (If(First(), processClassV),),\
                      lambda s, p, o: (None, TYPE,  s))

        #classVisitor = And(first, queryV)
        classVisitor = And(processClassV, queryV)

        self.query(classVisitor, None, TYPE, CLASS)
        
    def parentTypesV(self, type, processType):
        self.visit(lambda s, p, o, processType=processType: processType(o),\
                   type, SUBCLASSOF, None)

    def propertyValuesV(self, subject, processPropertyValue):
        def callbackAdaptor(s, p, o, processPropertyValue=processPropertyValue):
            processPropertyValue(p, o)            
        self.visit(callbackAdaptor, subject, None, None)

    def subClassV(self, type, processClass, processInstance, currentDepth=0, recurse=1):
        processClass(type, currentDepth, recurse)

        if recurse:
            query = Query(self.subClassV, (), lambda s, p, o: (s,), (processClass, processInstance, currentDepth+1))
        else:
            query = Query(processClass, (), lambda s, p, o: (s,), (currentDepth+1, 0))
        self.query(query, None, SUBCLASSOF, type)
        
        instanceQuery = Query(processInstance, (), lambda s, p, o: (s,), (currentDepth, recurse))
        self.query(instanceQuery, None, TYPE, type)


    # REIFICATION STUFF

    def reifiedV(self, subject, processStatement):
        for statement in self.getByType(STATEMENT, SUBJECT, subject):
            processStatement(statement[0], self.get(statement[0], PREDICATE, None)[0][2], self.get(statement[0], OBJECT, None)[0][2])

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

    def getPossibleValues(self, property):
        resultset = {}

        def possibleSubject(subject, property, value, resultset=resultset):
            resultset[subject] = 1

        self.getPossibleValuesV(property, possibleSubject)

        return resultset.keys()
        
    # callback may be called more than once for the same possibleValue... user
    # of this method will have to remove duplicates
    def getPossibleValuesV(self, property, possibleValue):        
        def rangeitem(s, p, o, self=self, qstore=self, possibleValue=possibleValue):
            for type in qstore.transitiveSubTypes(o):
                qstore.visit(possibleValue, None, TYPE, type)

        query = Query(rangeitem, (), lambda s, p, o: (s, p, o), (self, self, possibleValue))

        self.query(query, property, RANGE, None)
        #self.visit(rangeitem, property, RANGE, None)
        
    def getPossibleProperties(self, type, possibleProperty):
        for superType in self.transitiveSuperTypes(type):
            self.visit(possibleProperty, None, DOMAIN, superType)

    def visitTypes(self, callback, subject=None):
        self.visit(callback, subject, TYPE, None)

    def getPossiblePropertiesForSubject(self, subject, possibleProperty):
        def type(s, p, o, self=self, possibleProperty=possibleProperty):
            self.getPossibleProperties(o, possibleProperty)
        self.visitTypes(type, subject)
        # all subjects can take the properties that resource can
        # note: this will definitely lead to duplicates, but they are
        # possible anyway
        self.getPossibleProperties(RESOURCE, possibleProperty)

    def getRange(self, property):
        statement = self.getFirst(property, RANGE, None)
        if statement!=None:
            return statement[2]
        else:
            return None

    def query(self, visitor, subject=None, predicate=None, object=None):
        self.visit(visitor.visit, subject, predicate, object)
        visitor.flush()
        
    def get(self, subject=None, predicate=None, object=None):
        listBuilder = ListBuilder()
        self.query(listBuilder, subject, predicate, object)
	return listBuilder.list

    def getByType(self, type, predicate, object):
        listBuilder = ListBuilder()
        query = Query(self.query, (listBuilder,), lambda s, p, o: (s,), (predicate, object))
        self.query(query, None, TYPE, type)
        return listBuilder.list

    def label(self, subject, default=None):
        statement = Statement()
        self.query(First(statement), subject, LABEL, None)
        if statement.object():
            return un_literal(statement.object())
        elif default!=None:
            return default
        else:
            return subject

    def getFirst(self, subject, predicate, object):
        listBuilder = ListBuilder()
        self.query(First(listBuilder), subject, predicate, object)
        list = listBuilder.list
        if len(list)>0:
            return list[0]
        else:
            return None

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
        print s
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
    def __init__(self, query, pre, adapter, post=()):
        self.query = query
        self.adapter = adapter
        self.pre = pre
        self.post = post

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
    def __init__(self, query, pre, adapter, post, label):
        self.query = query
        self.adapter = adapter
        self.pre = pre
        self.post = post
        self.statements = {}
        self.label = label

    def visit(self, s, p, o):
        label = self.label(s, '')
        self.statements[label+s] = (s, p, o)

    def flush(self):
        keys = self.statements.keys()
        keys.sort()
        for k in keys:
            s, p, o = self.statements[k]
            apply(self.query, self.pre + self.adapter(s, p, o) + self.post)

#~ $Log$
#~ Revision 5.7  2000/12/10 07:44:59  eikeon
#~ refactored label to use new query method; still have a few thoughts before we go nuts and convert everything over
#~
#~ Revision 5.6  2000/12/10 06:54:39  eikeon
#~ refactored getFirst to use new query method
#~
#~ Revision 5.5  2000/12/10 06:39:52  eikeon
#~ refactored get to use new query method
#~
#~ Revision 5.4  2000/12/10 06:27:32  eikeon
#~ added adapter method query
#~
#~ Revision 5.3  2000/12/09 23:48:30  eikeon
#~ Added visitSubjects subject for conv. and efficiency
#~
#~ Revision 5.2  2000/12/09 21:32:16  jtauber
#~ all subjects can take the properties that RESOURCE can
#~
#~ Revision 5.1  2000/12/09 18:37:15  jtauber
#~ added typelessResources() query
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
