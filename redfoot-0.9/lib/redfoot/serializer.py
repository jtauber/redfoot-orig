# $Header$

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

    def __init__(self):
        self.namespaces = {}
        self.namespaceCount = 0

    def setStream(self, stream):
        self.stream = stream


    def setBase(self, base):
        self.base = base

    def registerProperty(self, property):
        uri = splitProperty(property)[0]
        if not self.namespaces.has_key(uri):
            self.namespaceCount = self.namespaceCount + 1
            prefix = "n%s" % self.namespaceCount
            self.namespaces[uri] = prefix

    def start(self):
        if not self.rdfns in self.namespaces.keys():
            self.namespaces[self.rdfns] = 'rdf'

        # TODO: workaround for browsers using iso-8859-1 character encoding
        self.stream.write( """<?xml version="1.0" encoding="iso-8859-1"?>\n""" )
        
        self.stream.write( "<%s:RDF\n" % self.namespaces[self.rdfns])
        for uri in self.namespaces.keys():
            self.stream.write( "   xmlns:%s=\"%s\"\n" % (self.namespaces[uri],uri) )
        self.stream.write( ">\n" )

    def end(self):
        self.stream.write( "</%s:RDF>\n" % self.namespaces[self.rdfns] )

    def subjectStart(self, subject):
        self.stream.write( "  <%s:Description" % self.namespaces[self.rdfns] )
        if subject[0:len(self.base)+1]==self.base+"#":
            self.stream.write( " %s:ID=\"%s\">\n" % (self.namespaces[self.rdfns], subject[len(self.base)+1:]) )
        else:
            self.stream.write( " %s:about=\"%s\">\n" % (self.namespaces[self.rdfns], subject) )

    def subjectEnd(self):
        self.stream.write( "  </%s:Description>\n" % self.namespaces[self.rdfns] )

    def property(self, predicate, value):
        def encode(s):
            import string
            s = string.join(string.split(s, '&'), '&amp;')
            s = string.join(string.split(s, '<'), '&lt;')
            s = string.join(string.split(s, '>'), '&gt;')
            s = string.join(string.split(s, '"'), '&quot;')
            return s

        (namespace, localName) = splitProperty(predicate)
        if value[0] == "^":
            self.stream.write( "    <%s:%s>%s</%s:%s>\n" % (self.namespaces[namespace], localName, encode(value[1:]), self.namespaces[namespace], localName) )
        else:
            if value[0:len(self.base)+1]==self.base+"#":
                value = value[len(self.base):]
            self.stream.write( "    <%s:%s %s:resource=\"%s\"/>\n" % (self.namespaces[namespace], localName, self.namespaces[self.rdfns], value) )


# $Log$
# Revision 2.0  2000/10/14 01:14:04  jtauber
# next version
#
# Revision 1.9  2000/10/09 21:57:42  eikeon
# made a fix to the encoding of special XML characters; added encoding declaration, as work around for now, to handle special characters comming from browsers
#
# Revision 1.8  2000/10/06 03:06:32  eikeon
# added missing return statement that was causing None for literal values
#
# Revision 1.7  2000/10/01 07:19:22  eikeon
# fixed output to encode &'s, <'s and ''s
#
