# $Header$
from rdf.literal import literal, un_literal, is_literal
        
class QueryStore:

    TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    CLASS = "http://www.w3.org/2000/01/rdf-schema#Class"
    PROPERTY = "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"
    RESOURCE = "http://www.w3.org/2000/01/rdf-schema#Resource"
    SUBCLASSOF = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
    LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
    COMMENT = "http://www.w3.org/2000/01/rdf-schema#comment"
    RANGE = "http://www.w3.org/2000/01/rdf-schema#range"
    DOMAIN = "http://www.w3.org/2000/01/rdf-schema#domain"
    LITERAL = "http://www.w3.org/2000/01/rdf-schema#Literal"
    STATEMENT = "http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement"
    SUBJECT = "http://www.w3.org/1999/02/22-rdf-syntax-ns#subject"
    PREDICATE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate"
    OBJECT = "http://www.w3.org/1999/02/22-rdf-syntax-ns#object"

    def label(self, subject, default=None):
        list = []
        def callback(subject, property, value, list=list):
            list.append((subject, property, value))
            return 0 # tell the visitor to stop
        
        self.visit(callback, subject, QueryStore.LABEL, None)

        if len(list) > 0:
            return un_literal(list[0][2])     # TODO: currently only returns first label
        else:
            return subject

    def comment(self, subject, default=None):
        list = []
        def callback(subject, property, value, list=list):
            list.append((subject, property, value))
            return 0 # tell the visitor to stop
        
        self.visit(callback, subject, QueryStore.COMMENT, None)

        if len(list) > 0:
            return un_literal(list[0][2])     # TODO: currently only returns first label
        else:
            return subject

    def getByType(self, type, predicate, object):
        l = []
        for s in self.get(None, QueryStore.TYPE, type):
            l.extend(self.get(s[0], predicate, object))
        return l

    def isKnownResource(self, resource):
        # TODO: can be made more efficient if can access hash directly
        if len(self.getProperties(resource)) > 0:
            return 1
        else:
            return 0

    # TODO: should we have a version of this that answers for subclasses too?
    def isOfType(self, resource, type):
        for s in self.get(resource, QueryStore.TYPE, None):
            if s[2] == type:
                return 1
        return 0

    def getSubjects(self):
        result = {}

        def subject(s, p, o, result=result):
            result[s] = 1
        
        self.visit(subject, None, None, None)

        return result.keys()

    def getProperties(self, subject=None):
        result = {}
        for s in self.get(subject, None, None):
            result[s[1]] = 1
        return result.keys()

    def getValues(self, subject, property):
        result = {}
        for s in self.get(subject, property, None):
            result[s[2]] = 1
        return result.keys()

    #TODO: remove typeInh as it is no longer being used
    def typeInh(self, t):
        l = []
        for s in self.get(t, QueryStore.SUBCLASSOF, None):
            l.extend(self.typeInh(s[2]))
        return [t,l]

    def transitiveSuperTypes(self, type):
        set = {}
        set[type] = 1

        for subclassStatement in self.get(type, QueryStore.SUBCLASSOF, None):
            for item in self.transitiveSuperTypes(subclassStatement[2]):
                set[item] = 1

        return set.keys()

    def transitiveSubTypes(self, type):
        set = {}
        set[type] = 1

        for subclassStatement in self.get(None, QueryStore.SUBCLASSOF, type):
            for item in self.transitiveSubTypes(subclassStatement[0]):
                set[item] = 1

        return set.keys()

    def rootClasses(self):
        """returns those classes that aren't a subclass of anything"""
        result = []
        for klass in self.get(None, QueryStore.TYPE, QueryStore.CLASS):
            if len(self.get(klass[0], QueryStore.SUBCLASSOF, None))==0:
                result.append(klass[0])
        return result
                
    # visitor pattern
    def resourcesByClassV(self, processClass, processResource):
        for klass in self.get(None, QueryStore.TYPE, QueryStore.CLASS):
            first = 1
            for resource in self.get(None, QueryStore.TYPE, klass[0]):
                if first:
                    processClass(klass[0])
                    first = 0
                processResource(resource[0])

    def parentTypesV(self, type, processType):
        self.visit(lambda s, p, o, processType=processType: processType(o),\
                   type, QueryStore.SUBCLASSOF, None)

    def propertyValuesV(self, subject, processPropertyValue):
        def callbackAdaptor(s, p, o, processPropertyValue=processPropertyValue):
            processPropertyValue(p, o)            
        self.visit(callbackAdaptor, subject, None, None)

    def subClassV(self, type, processClass, processInstance, currentDepth=0, recurse=1):
        processClass(type, currentDepth, recurse)
        def subclassStatement(s, p, o, \
                              processClass=processClass, \
                              processInstance=processInstance, \
                              currentDepth=currentDepth,
                              recurse=recurse,
                              self=self):
            if recurse:
                self.subClassV(s, processClass, processInstance, currentDepth+1)
            else:
                processClass(s, currentDepth+1, recurse)                
        self.visit(subclassStatement, None, QueryStore.SUBCLASSOF, type)
        def instanceStatement(s, p, o, \
                              currentDepth=currentDepth, \
                              recurse=recurse, \
                              processInstance=processInstance):
            processInstance(s, currentDepth, recurse)            
        self.visit(instanceStatement, None, QueryStore.TYPE, type)
    
    # REIFICATION STUFF

    def reifiedV(self, subject, processStatement):
        for statement in self.getByType(QueryStore.STATEMENT, QueryStore.SUBJECT, subject):
            processStatement(statement[0], self.get(statement[0], QueryStore.PREDICATE, None)[0][2], self.get(statement[0], QueryStore.OBJECT, None)[0][2])

    # should perhaps just autogenerate statement_uri
    def reify(self, statement_uri, subject, predicate, object):
        self.add(statement_uri, QueryStore.TYPE, QueryStore.STATEMENT)
        self.add(statement_uri, QueryStore.SUBJECT, subject)
        self.add(statement_uri, QueryStore.PREDICATE, predicate)
        self.add(statement_uri, QueryStore.OBJECT, object)

    # TODO: not sure this makes sense to have - jkt
    def dereify(self, statement_uri):
        subject = self.get(statement, QueryStore.SUBJECT, None)[0][2]
        predicate = self.get(statement, QueryStore.PREDICATE, None)[0][2]
        object = self.get(statement, QueryStore.OBJECT, None)[0][2]
        self.add(subject, predicate, object)
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
                qstore.visit(possibleValue, None, QueryStore.TYPE, type)

        self.visit(rangeitem, property, QueryStore.RANGE, None)
        


#~ $Log$
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
#~
#~ Revision 3.1  2000/11/02 21:48:27  eikeon
#~ removed old log messages
#~
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
