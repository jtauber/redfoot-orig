# TODO: move all or at least most of these to redfoot/xml/

from string import join, split, letters, digits

def encode_URI(s, safe='/'):
    always_safe = letters + digits + ' _,.-'
    safe = always_safe + safe
    res = []
    s = str(s) # in case s is not already a string
    for c in s:
        if c not in safe:
            res.append('%%%02x'%ord(c))
        else:
            if c==' ':
                res.append('+')
            else:
                res.append(c)
    return join(res, '')

def encode_attribute_value(s):
    s = str(s) # in case s is not already a string   
    s = join(split(s, '&'), '&amp;')
    s = join(split(s, '"'), '&quot;')
    #s = join(split(s, "'"), '&apos;')
    s = join(split(s, '<'), '&lt;')
    #We need not encode > for attributes
    #s = join(split(s, '>'), '&gt;')        
    return s

def encode_character_data(s):
    s = str(s) # in case s is not already a string
    s = join(split(s, '&'), '&amp;')
    s = join(split(s, '<'), '&lt;')
    return s

def escape_newlines(s, other="'"):
    """Used to escape newlines and by default 's"""
    s = str(s)
    for c in other:
        s = join(split(s, c), "\\"+c)
    s = join(split(s, "\n"), "\\n")
    return s

from time import time, gmtime


def date_time():
    t = time()    
    year, month, day, hh, mm, ss, wd, y, z = gmtime(t)
    s = "%0004d/%02d/%02dT%02d:%02d:%02dZ" % ( year, month, day, hh, mm, ss)
    return s

def to_URL(module_name, path):
    import sys, urlparse
    from os.path import join, dirname
    from urllib import pathname2url
    if urlparse.urlparse(path)[0] == '':
        libDir = dirname(sys.modules[module_name].__file__)
        return pathname2url(join(libDir, path))
    else: # path is absolute URL
        return path
