# $Header$

class StoreIO:

    def setStore(self, store):
        self.store = store

    def getStore(self):
        return self.store

    def visit(self, callback, subject=None, property=None, value=None):
        self.getStore().visit(callback, subject, property, value)
        
    def get(self, subject=None, property=None, value=None):
        return self.getStore().get(subject, property, value)

    def remove(self, subject=None, property=None, value=None):
        self.getStore().remove(subject, property, value)

    def add(self, subject, property, value):
        self.getStore().add(subject, property, value)

    def load(self, location, URI=None):
        self.location = location
        if URI==None:
            # default to location
            self.URI = self.location
        else:
            self.URI = URI

        from rdf.parser import RDFParser
        rdfParser = RDFParser()
        rdfParser.setAdder(self.store.add)

        rdfParser.parse(self.location, self.URI)

    def save(self):
        self.saveAs(self.location, self.URI)

    def saveAs(self, location, URI):
        stream = open(location, 'w')
        self.output(stream, URI)
        stream.close()
        
    def output(self, stream, URI=None):

        if URI==None:
            URI = self.URI

        from rdf.query import QueryStore
        queryStore = QueryStore()
        queryStore.setStore(self.getStore())
        
        from rdf.serializer import Serializer
        s = Serializer()

        s.setStream(stream)
        s.setBase(URI)

        properties = queryStore.getProperties()

        for property in properties:
            s.registerProperty(property)

        s.start()
        
        subjects = queryStore.getSubjects()
        subjects.sort() 

        for subject in subjects:
            s.subjectStart(subject)

            properties = queryStore.getProperties(subject)
            properties.sort()
            
            for property in properties:
                values = queryStore.getValues(subject, property)
                values.sort()
                
                for value in values:
                    s.property(property, value)

            s.subjectEnd()
        
        s.end()


#~ $Log$
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
