def encodeURI(s):
    import string
    return string.join(string.split(s,'#'),u'%23')

def generateURI():
    import time
    t = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(t)
    s = "%0004d/%02d/%02d/T%02d/%02d/%02dZ" % ( year, month, day, hh, mm, ss)
    return s

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
