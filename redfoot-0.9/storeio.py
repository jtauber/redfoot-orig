from redfoot.store import *
from redfoot.parser import *

class StoreIO:

    def setStore(self, store):
        self.store = store

    def getStore(self):
        return self.store

    def load(self, location, URI):
        self.location = location
        self.URI = URI
        rdfParser = RDFParser()
        rdfParser.setAdder(store.add)

        rdfParser.parser(self.location, self.URI)

    def save(self):
        self.saveAs(self.location, self.URI)

    def saveAs(self, location, URI):
        pass #TODO
