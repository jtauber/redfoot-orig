# $Header$
from rdf.literal import literal, un_literal, is_literal

from rdf.const import *

class QueryStore:

    def query(self, visitor, subject=None, predicate=None, object=None):
        self.visit(visitor.visit, subject, predicate, object)
        visitor.flush()
        
    def get(self, subject=None, predicate=None, object=None):
        list = []
        
        def callback(subject, predicate, object, list=list):
            list.append((subject, predicate, object))

        self.visit(callback, subject, predicate, object)

	return list

    def getFirst(self, subject, predicate, object):
        statements = []
        def callback(subject, predicate, object, statements=statements):
            statements.append((subject, predicate, object))
            return 1 # tell visitor to stop
        self.visit(callback, subject, predicate, object)
        if len(statements)>0:
            return statements[0]
        else:
            return None

    def label(self, subject, default=None):
        statement = self.getFirst(subject, LABEL, None)
        if statement!=None:
            return un_literal(statement[2])
        elif default!=None:
            return default
        else:
            return subject

     # TODO: method to return all labels
     
    def comment(self, subject, default=None):
        statement = self.getFirst(subject, COMMENT, None)
        if statement!=None:
            return un_literal(statement[2])
        elif default!=None:
            return default
        else:
            return self.label(subject)

    def getByType(self, type, predicate, object):
        statements = []
        def add(subject, predicate, object, statements=statements):
            statements.append((subject, predicate, object))
        def subjects(s, p, o, predicate=predicate, object=object, add=add, store=self):
            store.visit(add, s, predicate, object)
        self.visit(subjects, None, TYPE, type)
        return statements

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

    def getSubjects(self):
        result = {}
        def subject(s, p, o, result=result):
            result[s] = 1
        self.visit(subject, None, None, None)
        return result.keys()

    def getProperties(self, subject=None):
        result = {}
        def property(s, p, o, result=result):
            result[p] = 1
        self.visit(property, subject, None, None)
        return result.keys()

    def getValues(self, subject=None, property=None):
        result = {}
        def object(s, p, o, result=result):
            result[o] = 1
        self.visit(object, subject, property, None)
        return result.keys()

    def transitiveSuperTypes(self, type):
        set = {}
        set[type] = 1

        def callback(s, p, o, set=set, self=self):
            for item in self.transitiveSuperTypes(o):
                set[item] = 1
        self.visit(callback, type, SUBCLASSOF, None)

        return set.keys()

    def transitiveSubTypes(self, type):
        set = {}
        set[type] = 1

        def callback(s, p, o, set=set, self=self):
            for item in self.transitiveSubTypes(s):
                set[item] = 1
        self.visit(callback, None, SUBCLASSOF, type)

        return set.keys()

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
        def klass(s, p, o, processClass=processClass, processResource=processResource, self=self):
            if self.getFirst(None, TYPE, s)!=None:
                processClass(s)
            def resource(s, p, o, processClass=processClass,\
                         processResource=processResource, self=self):
                processResource(s)
            self.visit(resource, None, TYPE, s)
        self.visit(klass, None, TYPE, CLASS)
                

    def parentTypesV(self, type, processType):
        self.visit(lambda s, p, o, processType=processType: processType(o),\
                   type, SUBCLASSOF, None)

    def propertyValuesV(self, subject, processPropertyValue):
        def callbackAdaptor(s, p, o, processPropertyValue=processPropertyValue):
            processPropertyValue(p, o)            
        self.visit(callbackAdaptor, subject, None, None)

    def subClassV(self, type, processClass, processInstance, currentDepth=0, recurse=1):
        processClass(type, currentDepth, recurse)
        def subclass(s, p, o, self=self, currentDepth=currentDepth, recurse=recurse,\
                     processClass=processClass, processInstance=processInstance):
            if recurse:
                self.subClassV(s, processClass, processInstance, currentDepth+1)
            else:
                processClass(s, currentDepth+1, recurse)
        # show classes in neighbourhood as well
        self.visit(subclass, None, SUBCLASSOF, type)
        def instance(s, p, o, processInstance=processInstance, \
                     currentDepth=currentDepth, recurse=recurse):
            processInstance(s, currentDepth, recurse)
        # only show local instances
        self.visit(instance, None, TYPE, type)

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

        self.visit(rangeitem, property, RANGE, None)
        
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


#~ $Log$
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
#~
#~ Revision 4.20  2000/12/08 08:08:52  eikeon
#~ fixed getByType; fixed references to constants
#~
#~ Revision 4.19  2000/12/08 07:46:01  jtauber
#~ fixed bug in reification (part 1)
#~
#~ Revision 4.18  2000/12/08 07:25:52  jtauber
#~ fixed bug in reification where add needed to be local.add
#~
#~ Revision 4.17  2000/12/07 19:57:03  eikeon
#~ changed getTypes to visitTypes and made argument order etc more consistent with others
#~
#~ Revision 4.16  2000/12/06 21:45:13  eikeon
#~ refactored gets to visits in subClassV and resourcesByClassV
#~
#~ Revision 4.15  2000/12/06 21:22:40  eikeon
#~ added getRange function
#~
#~ Revision 4.14  2000/12/06 20:49:38  eikeon
#~ decomposed getPossibleProperties into two methods... one that takes a subject and the other that takes a type... also added a getTypes method
#~
#~ Revision 4.13  2000/12/06 20:10:04  eikeon
#~ added getPossibleProperties method
#~
#~ Revision 4.12  2000/12/06 19:42:39  eikeon
#~ moved get method to query as it can be layered on top of a TripleStore like all the other queries; reimplemented transitive{Super,Sub}Types to use visit
#~
#~ Revision 4.11  2000/12/06 06:00:02  eikeon
#~ minor fix to unused methods
#~
#~ Revision 4.10  2000/12/06 05:51:05  eikeon
#~ refactored some more gets to visits
#~
#~ Revision 4.9  2000/12/06 01:35:59  eikeon
#~ reimplemented isKnownResource
#~
#~ Revision 4.8  2000/12/05 23:40:32  eikeon
#~ reimplemented getByType to use visit
#~
#~ Revision 4.7  2000/12/05 23:12:00  eikeon
#~ factored out common getFirst functionality from label and comment
#~
#~ Revision 4.6  2000/12/05 22:09:36  jtauber
#~ moved constants to new file
#~
#~ Revision 4.5  2000/12/05 03:49:07  eikeon
#~ changed all the hardcoded [1:] etc stuff to use un_literal is_literal etc
#~
#~ Revision 4.4  2000/12/05 00:02:25  eikeon
#~ fixing some of the local / neighbourhood stuff
#~
#~ Revision 4.3  2000/12/04 22:00:57  eikeon
#~ got rid of all the getStore().getStore() stuff by using Multiple inheritance and mixin classes instead of all the classes being wrapper classes
#~
#~ Revision 4.2  2000/11/27 19:39:08  eikeon
#~ editor now alphabetically sort possible values for properties
#~
#~ Revision 4.1  2000/11/21 17:34:31  jtauber
#~ reify no longer removes original triple
#~
#~ Revision 4.0  2000/11/06 15:57:33  eikeon
#~ VERSION 4.0
