from redfootlib.util import encode_attribute_value, encode_character_data

# TODO: really needs to be fully unicode
namestart = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
             'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
             'a','b','c','d','e','f','g','h','i','j','k','l','m',
             'n','o','p','q','r','s','t','u','v','w','x','y','z',
             '_']

namechars = namestart + ['0','1','2','3','4','5','6','7','8','9','-','.']


def split_property(property):
    property = property
    length = len(property)
    for i in xrange(1, length):
        if not property[-i-1] in namechars:
            for j in xrange(-1-i,length):
                if property[j] in namestart:
                    return (property[:j], property[j:])
    return ("", property)


    
class Serializer(object):
    """RDF serializer.
    
    To set up the serializer, set_stream and set_base_URI are
    called. This is followed by register_property being called for
    each property. The serialization is started with start and ended
    with end. Between start and end, there are two options:

    - call start_subject, call property one or more times, call
      end_subject
    - call triple for each statement

    The former is a little lower level but provided for cases where it
    would be more efficient.
    """
    
    rdfns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    rdfsns = "http://www.w3.org/2000/01/rdf-schema#"    

    def __init__(self):
        super(Serializer, self).__init__()
        
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
        uri = split_property(property)[0]        
        if not self.namespaces.has_key(uri):
            self.namespaceCount = self.namespaceCount + 1
            prefix = "n%s" % self.namespaceCount
            self.namespaces[uri] = prefix

    def start(self):
        # TODO: workaround for browsers using iso-8859-1 character encoding
        self.stream.write( """<?xml version="1.0" encoding="UTF-8"?>\n""" )
        
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
        if self.baseURI and subject[0:len(self.baseURI)+1]==self.baseURI+"#":
            self.stream.write( " rdf:ID=\"%s\">\n" % subject[len(self.baseURI)+1:])       
        else:
            self.stream.write( " rdf:about=\"%s\">\n" % encode_attribute_value(subject) )
    def subject_end(self):
        self.current_subject = None
        self.stream.write( "  </rdf:Description>\n" )

    def property(self, predicate, object, literal_object=0):
        (namespace, localName) = split_property(predicate)   
        prefix = self.namespaces[namespace]

        # TODO: Is this what we want to do if object is None?
        if object==None or object=="":
            object = ""
            literal_object = 1
            
        if literal_object:
            self.stream.write( "    <%s:%s>%s</%s:%s>\n" % (prefix, localName, encode_character_data(object), prefix, localName) )
        else:
            if self.baseURI and object[0:len(self.baseURI)+1]==self.baseURI+"#":
                object = object[len(self.baseURI):]
            self.stream.write( "    <%s:%s rdf:resource=\"%s\"/>\n" % (prefix, localName, encode_attribute_value(object)) )            

    # TODO: the following might not work with anonymous containers
    def triple(self, subject, predicate, object, literal_object):
        if self.current_subject != subject:
            if self.current_subject != None:
                self.subject_end()
            self.subject_start(subject)
            self.current_subject = subject
        self.property(predicate, object, literal_object)


class RedSerializer(Serializer, object):

    def __init__(self):
        super(RedSerializer, self).__init__()
    
    def triple(self, s, p, o):
        try:
            if o.is_literal():
                Serializer.triple(self, s, p, o, 1)
            else:
                Serializer.triple(self, s, p, o, 0)
        except:
            # TODO: could write out as literal in this case?
            print "WARNING: ignoring (%s, %s, %s)" % (s, p, o)

    def register_property(self, s, p, o):
        return Serializer.register_property(self, p)

    def output(self, stream, URI=None, subject=None, predicate=None, object=None, absolute=0):
        if URI==None:
            URI = self.baseURI

        self.set_stream(stream)
        if absolute!=1:
            self.set_base_URI(URI)

        self.visit(self.register_property, (subject, predicate, object))

        self.start()
        self.visit(self.triple, (subject, predicate, object))
        self.end()
