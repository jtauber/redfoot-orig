# $Header$
from rdf.literal import literal, un_literal, is_literal
from rdf.const import *

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
        query = Query(self.query, (listBuilder,), lambda s, p, o: (s,), (predicate, object))
        self.query(query, None, TYPE, type)
        return listBuilder.list

    def visitByType(self, visitor, type, predicate, object):
        query = Query(self.query, (visitor,), lambda s, p, o: (s,), (predicate, object))
        self.query(query, None, TYPE, type)

    def visitResourcesByType_orig(self, type_callback, resource_callback):
        resourceVisitor = Query(resource_callback, (), lambda s, p, o: (s,))
        queryV = Query(self.query, (resourceVisitor,), lambda s, p, o: (None, TYPE, s))

        typeVisitor = Query(type_callback, (), lambda s, p, o: (s,))

        classVisitor = And(typeVisitor, queryV)

        self.query(classVisitor, None, TYPE, CLASS)

    def visitResourcesByType(self, processClass, processResource):
        setBuilder = ObjectSetBuilder()
        self.query(setBuilder, None, TYPE, None)
        types = setBuilder.set.keys()
        for klass in types:
            if self.getFirst(None, TYPE, klass)!=None:
                processClass(klass)
                def resource(s, p, o, processClass=processClass,\
                             processResource=processResource, self=self):
                    processResource(s)
                self.visit(resource, None, TYPE, klass)

        
    def visitPredicateObjectPairsForSubject(self, predicateObject_callback, subject):
        def callbackAdaptor(s, p, o, predicateObject_callback=predicateObject_callback):
            predicateObject_callback(p, o)            
        self.visit(callbackAdaptor, subject, None, None)

    # REIFICATION STUFF

    def visitReifiedStatementsAboutSubject(self, callback, subject):
        def adapter(callback, subject, getFirst):
            callback(subject, getFirst(subject, PREDICATE, None)[2], getFirst(subject, OBJECT, None)[2])

        visitor = Query(adapter, (callback,), lambda s, p, o: (s,), (self.getFirst,))
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
        trans = And(callback, Query(self.visitTransitiveSuperTypes, (callback,), lambda s, p, o: (o,)))
        self.query(trans, type, SUBCLASSOF, None)

    def getTransitiveSubTypes(self, type):
        objectSetBuilder = ObjectSetBuilder()
        objectSetBuilder.set[type] = 1
        self.visitTransitiveSubTypes(objectSetBuilder, type)
        return objectSetBuilder.set.keys()

    def visitTransitiveSubTypes(self, callback, type):
        trans = And(callback, Query(self.visitTransitiveSubTypes, (callback,), lambda s, p, o: (s,)))
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
        self.visit(lambda s, p, o, callback=callback: callback(o),\
                   type, SUBCLASSOF, None)

    def visitSubclasses(self, class_callback, instance_callback, type, currentDepth=0, recurse=1):
        class_callback(type, currentDepth, recurse)

        if recurse:
            query = Query(self.visitSubclasses, (class_callback, instance_callback), lambda s, p, o: (s,), (currentDepth+1,))
        else:
            query = Query(class_callback, (), lambda s, p, o: (s,), (currentDepth+1, 0))
        self.query(query, None, SUBCLASSOF, type)
        
        instanceQuery = Query(instance_callback, (), lambda s, p, o: (s,), (currentDepth, recurse))
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
        def rangeitem(s, p, o, self=self, qstore=self, callback=callback):
            for type in qstore.getTransitiveSubTypes(o):
                qstore.visit(callback, None, TYPE, type)

        query = Query(rangeitem, (), lambda s, p, o: (s, p, o), (self, self, callback))

        self.query(query, property, RANGE, None)

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
#~ Revision 5.13  2000/12/20 03:59:53  jtauber
#~ visitResourcesByType will now visit resources whose type is an unknown class
#~
#~ Revision 5.12  2000/12/17 20:56:08  eikeon
#~ renamed visitSubjects to visit_subjects
#~
#~ Revision 5.11  2000/12/14 05:14:39  eikeon
#~ removed unused gets
#~
#~ Revision 5.10  2000/12/14 00:22:37  eikeon
#~ fixed up *Transitive* methods
#~
#~ Revision 5.9  2000/12/13 02:54:11  jtauber
#~ moved functions in query around and renamed a lot
#~
#~ Revision 5.8  2000/12/13 00:43:11  eikeon
#~ half baked changes
#~
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
