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

# TODO: the following two functions are duplicated from parser

def literal(str):
    return "^"+str

def is_literal(str):
    return str[0]=="^"

def un_literal(str):
    return str[1:]

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

        # TODO: Is this what we want to do if value is None?
        if value==None or value=="":
            value = literal("")
            
        if is_literal(value):
            self.stream.write( "    <%s:%s>%s</%s:%s>\n" % (self.namespaces[namespace], localName, encode(un_literal(value)), self.namespaces[namespace], localName) )
        else:
            if value[0:len(self.base)+1]==self.base+"#":
                value = value[len(self.base):]
            self.stream.write( "    <%s:%s %s:resource=\"%s\"/>\n" % (self.namespaces[namespace], localName, self.namespaces[self.rdfns], value) )


#~ $Log$
#~ Revision 4.0  2000/11/06 15:57:33  eikeon
#~ VERSION 4.0
#~
#~ Revision 3.2  2000/11/04 01:24:50  eikeon
#~ fixed string index out of range bug in serializer
#~
#~ Revision 3.1  2000/11/02 21:48:27  eikeon
#~ removed old log messages
#~
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
