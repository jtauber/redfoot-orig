# $Header$

import string

# TODO: really needs to be fully unicode
namestart = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
             'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
             'a','b','c','d','e','f','g','h','i','j','k','l','m',
             'n','o','p','q','r','s','t','u','v','w','x','y','z',
             '_']

namechars = namestart + ['0','1','2','3','4','5','6','7','8','9','-','.']

def encode(s):
    s = string.join(string.split(s, '&'), '&amp;')
    s = string.join(string.split(s, '<'), '&lt;')
    s = string.join(string.split(s, '>'), '&gt;')
    s = string.join(string.split(s, '"'), '&quot;')
    return s

def split_property(property, namespaces):
    keys = namespaces.keys()
    for namespace in keys:
        if string.find(property, namespace)==0:
            return (namespace, property[len(namespace):])
    length = len(property)
    for i in range(length):
        if not property[-1-i] in namechars:
            for j in range(-1-i,length):
                if property[j] in namestart:
                    return (property[:j],property[j:])
    return ("",property)


from rdf.literal import *

class Serializer:
    rdfns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    rdfsns = "http://www.w3.org/2000/01/rdf-schema#"    

    def __init__(self):
        self.namespaces = {}
        self.namespaces[self.rdfns] = 'rdf'
        self.namespaces[self.rdfsns] = 'rdfs'        
        
        self.namespaceCount = 0
        self.current_subject = None
        self.baseURI = None

    def set_stream(self, stream):
        self.stream = stream

    def set_base_URI(self, baseURI):
        self.baseURI = baseURI

    def register_property(self, property):
        uri = split_property(property, self.namespaces)[0]
        if not self.namespaces.has_key(uri):
            self.namespaceCount = self.namespaceCount + 1
            prefix = "n%s" % self.namespaceCount
            self.namespaces[uri] = prefix

    def start(self):
        # TODO: workaround for browsers using iso-8859-1 character encoding
        self.stream.write( """<?xml version="1.0" encoding="iso-8859-1"?>\n""" )
        
        self.stream.write( "<rdf:RDF\n" )
        for uri in self.namespaces.keys():
            self.stream.write( "   xmlns:%s=\"%s\"\n" % (self.namespaces[uri],uri) )
        self.stream.write( ">\n" )

    def end(self):
        if self.current_subject != None:
            self.subject_end()
        self.stream.write( "</rdf:RDF>\n" )

    def subject_start(self, subject):
        self.stream.write( "  <rdf:Description" )
#        if self.baseURI and subject[0:len(self.baseURI)+1]==self.baseURI+"#":
        if self.baseURI and string.find(subject, self.baseURI+"#")==0:
            self.stream.write( " rdf:ID=\"%s\">\n" % subject[len(self.baseURI)+1:])       
        else:
            self.stream.write( " rdf:about=\"%s\">\n" % encode(subject) )            

    def subject_end(self):
        self.current_subject = None
        self.stream.write( "  </rdf:Description>\n" )

    def property(self, predicate, object):
        (namespace, localName) = split_property(predicate, self.namespaces)
        prefix = self.namespaces[namespace]

        # TODO: Is this what we want to do if object is None?
        if object==None or object=="":
            object = literal("")
            
        if is_literal(object):
            self.stream.write( "    <%s:%s>%s</%s:%s>\n" % (prefix, localName, encode(un_literal(object)), prefix, localName) )
        else:
            if self.baseURI and object[0:len(self.baseURI)+1]==self.baseURI+"#":
                object = object[len(self.baseURI):]
            self.stream.write( "    <%s:%s rdf:resource=\"%s\"/>\n" % (prefix, localName, encode(object)) )            

    def triple(self, subject, predicate, object):
        if self.current_subject != subject:
            if self.current_subject != None:
                self.subject_end()
            self.subject_start(subject)
            self.current_subject = subject
        self.property(predicate, object)

#~ $Log$
#~ Revision 6.1  2001/02/26 22:30:24  eikeon
#~ optimized split_property a bit by adding a cache lookup; also hard coded the rdf prefix
#~
#~ Revision 6.0  2001/02/19 05:01:23  jtauber
#~ new release
#~
#~ Revision 5.6  2000/12/20 20:37:17  eikeon
#~ changed mixed case to _ style... all except for query
#~
#~ Revision 5.5  2000/12/19 05:37:08  eikeon
#~ Serializer will now also work with no baseURI
#~
#~ Revision 5.4  2000/12/17 20:55:27  eikeon
#~ pulled len(property) out of loop
#~
#~ Revision 5.3  2000/12/17 20:41:22  eikeon
#~ removed log message prior to currently worked on release
#~
#~ Revision 5.2  2000/12/09 21:01:44  eikeon
#~ abouts were not getting encoded
#~
#~ Revision 5.1  2000/12/08 23:02:23  eikeon
#~ encoding fixes
#~
#~ Revision 5.0  2000/12/08 08:34:52  eikeon
#~ new release
