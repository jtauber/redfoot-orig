#from redfoot.store import *
from redfoot.parser import *

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
        
        s = Serializer()
        s.setBase(self.URI)

         
        s.registerProperty("foo#author")
        s.start()
        
        s.subjectStart("http://jtauber.com")
        s.property("foo#author","^James Tauber")
        s.subjectEnd()
        
        s.end()
