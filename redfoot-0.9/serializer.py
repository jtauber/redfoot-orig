# TODO: really needs to be fully unicode
namestart = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
             'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
             'a','b','c','d','e','f','g','h','i','j','k','l','m',
             'n','o','p','q','r','s','t','u','v','w','x','y','z',
             '_']

namechars = namestart + ['0','1','2','3','4','5','6','7','8','9','-','.']

def splitProperty(property):
    for i in range(len(property)):
        if not property[-1-i] in namechars:
            for j in range(-1-i,len(property)):
                if property[j] in namestart:
                    return (property[:j],property[j:])
    return ("",property)

class Serializer:
    rdfns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

    def setBase(self, base):
        self.base = base

    def registerProperty(self, property):
        self.namespaces = {}
        self.namespaceCount = 0

        uri = splitProperty(property)[0]
        if not uri in self.namespaces.keys():
            self.namespaceCount = self.namespaceCount + 1
            prefix = "n%s" % self.namespaceCount
            self.namespaces[uri] = prefix

    def start(self):
        if not self.rdfns in self.namespaces.keys():
            self.namespaces[self.rdfns] = 'rdf'

        print "<?xml version=\"1.0\"?>"
        print "<%s:RDF" % self.namespaces[self.rdfns]
        for uri in self.namespaces.keys():
            print "   xmlns:%s=\"%s\"" % (self.namespaces[uri],uri)
        print ">"

    def end(self):
        print "</%s:RDF>" % self.namespaces[self.rdfns]

    def subjectStart(self, subject):
        print "  <%s:Description" % self.namespaces[self.rdfns]
        if subject[0:len(self.base)+1]==self.base+"#":
            print "    %s:ID=\"%s\"" %
            (self.namespaces[self.rdfns], subject[len(self.base)+1:])
        else:
            print "    %s:about=\"%s\"" %
            (self.namespaces[self.rdfns], subject)

    def subjectEnd(self):
        print "  </%s:Description>" % self.namespaces[self.rdfns]

    def property(self, predicate, value):
            (namespace, localName) = splitProperty(predicate)
            if value[0] == "^":
                print "    <%s:%s>%s</%s:%s>" %
                (self.namespaces[namespace], localName,
                 value[1:],
                 self.namespaces[namespace], localName)
            else:
                if value[0:len(self.base)+1]==self.base+"#":
                    value = value[len(self.base):]
                print "    <%s:%s %s:resource=\"%s\"/>" %
                (self.namespaces[namespace], localName,
                 self.namespaces[self.rdfns], value)
