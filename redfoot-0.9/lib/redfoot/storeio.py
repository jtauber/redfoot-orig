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

        from redfoot.parser import RDFParser
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

        from redfoot.query import QueryStore
        queryStore = QueryStore()
        queryStore.setStore(self.getStore())
        
        from redfoot.serializer import Serializer
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


# $Log$
# Revision 2.1  2000/10/16 17:19:02  eikeon
# visit method now takes a callback function instead of a visitor object
#
# Revision 2.0  2000/10/14 01:14:04  jtauber
# next version
#
# Revision 1.14  2000/10/08 07:15:50  jtauber
# fixed bug where get on storeio was not returning
#
# Revision 1.13  2000/10/05 00:48:40  jtauber
# added remove and add methods which just call the corresponding methods on the store
#
# Revision 1.12  2000/10/01 03:58:10  eikeon
# fixed up all the places where I put CVS keywords as keywords in omments... duh
#
# Revision 1.11  2000/10/01 03:04:10  eikeon
# added visit and get method so that StoreIOs can be treated as Stores; changed output to use self.URI if no URI is passed in; added Header and Log CVS keywords
#