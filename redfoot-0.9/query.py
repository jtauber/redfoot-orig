
class QueryStore:

    TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    CLASS = "http://www.w3.org/2000/01/rdf-schema#Class"
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
            return l[0][2]     # TODO: currently only returns first label
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
        for s in model.store.get(resource, QueryStore.TYPE, None):
            if s[2] == type:
                return 1
        return 0

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
