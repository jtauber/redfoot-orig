# $Header$

from rdf.literal import *
import string

def encodeURI(s):
    return encode_URI(s)


def encode_attribute_value(s):
    s = string.join(string.split(s, '&'), '&amp;')
    s = string.join(string.split(s, '"'), '&quot;')
    return s

def encode_character_data(s):
    s = string.join(string.split(s, '&'), '&amp;')
    s = string.join(string.split(s, '&lt;'), '&lt;')
    return s

def encode_URI(s, safe='/'):
    always_safe = string.letters + string.digits + ' _,.-'
    safe = always_safe + safe
    res = []
    for c in s:
        if c not in safe:
            res.append('%%%02x'%ord(c))
        else:
            if c==' ':
                res.append('+')
            else:
                res.append(c)

    # TODO: check to see if joinfields has been replaced by
    # join... think it has.
    return string.joinfields(res, '')

def generateURI():
    import time
    t = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
    s = "%0004d/%02d/%02d/T%02d-%02d-%02dZ%0004d" % ( year, month, day, hh, mm, ss, serial_number() % 1000)
    return s

_serial_number = 0
def serial_number():
    global _serial_number
    _serial_number = _serial_number + 1
    return  _serial_number


def ignoreCaseSort(a, b):
    import string
    return cmp(string.lower(a), string.lower(b))

def date_time_filename(t=None):
    """."""
    import time
    if t==None:
        t = time.time()

    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
    s = "%0004d-%02d-%02dT%02d_%02d_%02dZ" % ( year, month, day, hh, mm, ss)        
    return s

def date_time(t=None):
    import time
    t = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
    s = "%0004d/%02d/%02dT%02d:%02d:%02dZ" % ( year, month, day, hh, mm, ss)
    return s

def filter_triples(triples, filter):
    list = []
    for triple in triples:
        if filter(triple)==0:
            list.append(triple)
    return list

def sort_triples(triples, sort):
    return triples


def get_property_value(rednode, subject, predicate, default="", resource=0):
    t = rednode.getFirst(subject, predicate, None)
    if t!=None:
        if resource:
            result = t[2]
        else:
            result = un_literal(t[2])
    else:
        result = default

    return result


def is_instance_of(rednode, resource, type):
    if resource==None:
        return 0
    for type in rednode.getTransitiveSubTypes(type):
        if rednode.isOfType(resource, type):
            return 1
    return 0

def get_instances_of(rednode, type):
    class StatementSetBuilder:
        def __init__(self):
            self.set = {}
        def visit(self, s, p, o):
            self.set[(s, p, o)] = 1
        def flush(self):
            pass

    visitor = StatementSetBuilder()
    ofTypeVisitor = Query(rednode.query, (visitor, lambda type, p, o: [None, TYPE, type]))
    rednode.visitTransitiveSubTypes(ofTypeVisitor, type)
    rednode.query(visitor, None, TYPE, type) # trans sub types must not include itself.
    return visitor.set.keys()

#~ $Log$
#~ Revision 8.1  2001/04/29 03:08:02  eikeon
#~ removed old log messages
#~
#~ Revision 8.0  2001/04/27 00:52:13  eikeon
#~ new release
