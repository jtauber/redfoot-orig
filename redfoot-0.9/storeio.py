#from redfoot.store import *
from redfoot.parser import *
from redfoot.query import QueryStore
from redfoot.serializer import Serializer

class StoreIO:

    def setStore(self, store):
        self.store = store

    def getStore(self):
        return self.store

    def load(self, location, URI=None):
        self.location = location
        if URI==None:
            # default to location
            self.URI = self.location
        else:
            self.URI = URI

        rdfParser = RDFParser()
        rdfParser.setAdder(self.store.add)

        rdfParser.parse(self.location, self.URI)

    def save(self):
        self.saveAs(self.location, self.URI)

    def saveAs(self, location, URI):
        
        queryStore = QueryStore()
        queryStore.setStore(self.getStore())
        
        s = Serializer()
        s.setLocation(location)
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

