
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

    def get(self, subject, predicate, object):
        return self.store.get(subject, predicate, object)

    def label(self, subject):
        l = self.get(subject, QueryStore.LABEL, None)
        if len(l) > 0:
            return l[0][2][1:]     # TODO: currently only returns first label
        else:
            return subject

    def comment(self, subject):
        c = self.get(subject, QueryStore.COMMENT, None)
        if len(c) > 0:
            return c[0][2]     # TODO: currently only returns first comment
        else:
            return self.label(subject)

    def getByType(self, type, predicate, object):
        l = []
        for s in self.get(None, QueryStore.TYPE, type):
            l.extend(self.get(s[0], predicate, object))
        return l

    def isOfType(self, resource, type):
        for s in self.store.get(resource, QueryStore.TYPE, None):
            if s[2] == type:
                return 1
        return 0

    def getSubjects(self):
        result = {}
        for s in self.store.get(None, None, None):
            result[s[0]] = 1
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

    # big data structure
    def resourcesByClass(self):
        result = {}
        for klass in self.store.get(None, QueryStore.TYPE, QueryStore.CLASS):
            result[klass[0]] = []
            for resource in self.store.get(None, QueryStore.TYPE, klass[0]):
                result[klass[0]].append(resource[0])
        return result
                
    # vistor pattern
    def resourcesByClassV(self, processClass, processResource):
        for klass in self.store.get(None, QueryStore.TYPE, QueryStore.CLASS):
            processClass(klass[0])
            for resource in self.store.get(None, QueryStore.TYPE, klass[0]):
                processResource(resource[0])

        
