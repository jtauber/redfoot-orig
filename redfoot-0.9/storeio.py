
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

        from redfoot.parser import RDFParser
        rdfParser = RDFParser()
        rdfParser.setAdder(self.store.add)

        rdfParser.parse(self.location, self.URI)

    def save(self):
        self.saveAs(self.location, self.URI)

    def saveAs(self, location, URI):
        
        from redfoot.query import QueryStore
        queryStore = QueryStore()
        queryStore.setStore(self.getStore())
        
        from redfoot.serializer import Serializer
        s = Serializer()

        try:
            stream = open(location, 'w')
        except IOError:
            print IOError

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

        stream.close()
