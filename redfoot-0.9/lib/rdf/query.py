# $Header$

class QueryStore:

    def __init__(self, store=None):
        if store!=None:
            self.store = store
    
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

    def setStore(self, store):
        self.store = store

    def getStore(self):
        return self.store

    def get(self, subject=None, predicate=None, object=None):
        return self.store.get(subject, predicate, object)

    def visit(self, callback, subject=None, predicate=None, object=None):
        self.store.visit(callback, subject, predicate, object)

    def label(self, subject):
        l = self.get(subject, QueryStore.LABEL, None)
        if len(l) > 0:
            return l[0][2][1:]     # TODO: currently only returns first label
        else:
            return subject

    def comment(self, subject):
        c = self.get(subject, QueryStore.COMMENT, None)
        if len(c) > 0:
            return c[0][2][1:]     # TODO: currently only returns first comment
        else:
            return self.label(subject)

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
        for s in self.store.get(resource, QueryStore.TYPE, None):
            if s[2] == type:
                return 1
        return 0

    def getSubjects(self):
        result = {}

        def subject(s, p, o, result=result):
            result[s] = 1
        
        self.store.visit(subject, None, None, None)

        return result.keys()

    def getProperties(self, subject=None):
        result = {}
        for s in self.store.get(subject, None, None):
            result[s[1]] = 1
        return result.keys()

    def getValues(self, subject, property):
        result = {}
        for s in self.store.get(subject, property, None):
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

        for subclassStatement in self.store.get(None, QueryStore.SUBCLASSOF, type):
            for item in self.transitiveSubTypes(subclassStatement[0]):
                set[item] = 1

        return set.keys()

    def rootClasses(self):
        """returns those classes that aren't a subclass of anything"""
        result = []
        for klass in self.store.get(None, QueryStore.TYPE, QueryStore.CLASS):
            if len(self.store.get(klass[0], QueryStore.SUBCLASSOF, None))==0:
                result.append(klass[0])
        return result
                
    # visitor pattern
    def resourcesByClassV(self, processClass, processResource):
        for klass in self.store.get(None, QueryStore.TYPE, QueryStore.CLASS):
            first = 1
            for resource in self.store.get(None, QueryStore.TYPE, klass[0]):
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
        self.store.visit(callbackAdaptor, subject, None, None)
            
    def propertyValuesLocalV(self, subject, processPropertyValue):
        def callbackAdaptor(s, p, o, processPropertyValue=processPropertyValue):
            processPropertyValue(p, o)
        self.store.store.visit(callbackAdaptor, subject, None, None)

    def propertyValuesNeighbourhoodV(self, subject, processPropertyValue):
        def callbackAdaptor(s, p, o, processPropertyValue=processPropertyValue):
            processPropertyValue(p, o)
        self.store.stores.visit(callbackAdaptor, subject, None, None)
        
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
        self.store.visit(subclassStatement, None, QueryStore.SUBCLASSOF, type)
        def instanceStatement(s, p, o, \
                              currentDepth=currentDepth, \
                              recurse=recurse, \
                              processInstance=processInstance):
            processInstance(s, currentDepth, recurse)            
        self.store.visit(instanceStatement, None, QueryStore.TYPE, type)
    
    # REIFICATION STUFF

    def reifiedV(self, subject, processStatement):
        for statement in self.getByType(QueryStore.STATEMENT, QueryStore.SUBJECT, subject):
            processStatement(statement[0], self.store.get(statement[0], QueryStore.PREDICATE, None)[0][2], self.store.get(statement[0], QueryStore.OBJECT, None)[0][2])

    # should perhaps just autogenerate statement_uri
    def reify(self, statement_uri, subject, predicate, object):
        self.store.add(statement_uri, QueryStore.TYPE, QueryStore.STATEMENT)
        self.store.add(statement_uri, QueryStore.SUBJECT, subject)
        self.store.add(statement_uri, QueryStore.PREDICATE, predicate)
        self.store.add(statement_uri, QueryStore.OBJECT, object)
        self.store.remove(subject, predicate, object)

    def dereify(self, statement_uri):
        subject = self.store.get(statement, QueryStore.SUBJECT, None)[0][2]
        predicate = self.store.get(statement, QueryStore.PREDICATE, None)[0][2]
        object = self.store.get(statement, QueryStore.OBJECT, None)[0][2]
        self.store.add(subject, predicate, object)
        #self.store.removeAll(statement)

    # TODO: NEED TO MAKE A VISITOR VERSION
    # If we want to remove duplicates the non visitor version is the best we can do? -eik
    def getPossibleValues(self, property):
        resultset = {}

        def possibleSubject(subject, property, value, resultset=resultset):
            resultset[subject] = 1

        def rangeitem(s, p, o, self=self, qstore=self, possibleSubject=possibleSubject):
            for type in qstore.transitiveSubTypes(o):
                qstore.visit(possibleSubject, None, QueryStore.TYPE, type)

        self.store.visit(rangeitem, property, QueryStore.RANGE, None)
        
        return resultset.keys()

#~ $Log$
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
