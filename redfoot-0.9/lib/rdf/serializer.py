# $Header$

# TODO: really needs to be fully unicode
namestart = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
             'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
             'a','b','c','d','e','f','g','h','i','j','k','l','m',
             'n','o','p','q','r','s','t','u','v','w','x','y','z',
             '_']

namechars = namestart + ['0','1','2','3','4','5','6','7','8','9','-','.']

def encode(s):
    import string
    s = string.join(string.split(s, '&'), '&amp;')
    s = string.join(string.split(s, '<'), '&lt;')
    s = string.join(string.split(s, '>'), '&gt;')
    s = string.join(string.split(s, '"'), '&quot;')
    return s

def splitProperty(property):
    for i in range(len(property)):
        if not property[-1-i] in namechars:
            for j in range(-1-i,len(property)):
                if property[j] in namestart:
                    return (property[:j],property[j:])
    return ("",property)


from rdf.literal import *

class Serializer:
    rdfns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

    def __init__(self):
        self.namespaces = {}
        self.namespaceCount = 0
        self.currentSubject = None

    def setStream(self, stream):
        self.stream = stream

    def setBaseURI(self, baseURI):
        self.baseURI = baseURI

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
        if self.currentSubject != None:
            self.subjectEnd()
        self.stream.write( "</%s:RDF>\n" % self.namespaces[self.rdfns] )

    def subjectStart(self, subject):
        self.stream.write( "  <%s:Description" % self.namespaces[self.rdfns] )
        if subject[0:len(self.baseURI)+1]==self.baseURI+"#":
            self.stream.write( " %s:ID=\"%s\">\n" % (self.namespaces[self.rdfns], subject[len(self.baseURI)+1:]) )
        else:
            self.stream.write( " %s:about=\"%s\">\n" % (self.namespaces[self.rdfns], encode(subject)) )

    def subjectEnd(self):
        self.currentSubject = None
        self.stream.write( "  </%s:Description>\n" % self.namespaces[self.rdfns] )

    def property(self, predicate, object):
        (namespace, localName) = splitProperty(predicate)

        # TODO: Is this what we want to do if object is None?
        if object==None or object=="":
            object = literal("")
            
        if is_literal(object):
            self.stream.write( "    <%s:%s>%s</%s:%s>\n" % (self.namespaces[namespace], localName, encode(un_literal(object)), self.namespaces[namespace], localName) )
        else:
            if object[0:len(self.baseURI)+1]==self.baseURI+"#":
                object = object[len(self.baseURI):]
            self.stream.write( "    <%s:%s %s:resource=\"%s\"/>\n" % (self.namespaces[namespace], localName, self.namespaces[self.rdfns], encode(object)) )

    def triple(self, subject, predicate, object):
        if self.currentSubject != subject:
            if self.currentSubject != None:
                self.subjectEnd()
            self.subjectStart(subject)
            self.currentSubject = subject
        self.property(predicate, object)

#~ $Log$
#~ Revision 5.2  2000/12/09 21:01:44  eikeon
#~ abouts were not getting encoded
#~
#~ Revision 5.1  2000/12/08 23:02:23  eikeon
#~ encoding fixes
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
