from __future__ import generators

from urlparse import urlparse        

from rdflib.syntax.parser import Parser
from rdflib.syntax.nt_parser import NTParser
from rdflib.syntax.serializer import Serializer

from rdflib.nodes import URIRef

from threading import Lock

from rdflib.nodes import URIRef

from time import time, gmtime

def generate_path():
    sn = 0
    last_time_path = None
    while 1:
        t = time()
        year, month, day, hh, mm, ss, wd, y, z = gmtime(t)           
        time_path = "%0004d/%02d/%02d/T%02d/%02d/%02dZ" % ( year, month, day, hh, mm, ss)

        if time_path==last_time_path:
            sn = sn + 1
        else:
            sn = 0
            last_time_path = time_path

        path = time_path + "%.004d" % sn
        yield path

path_generator = generate_path()


class LoadSave(NTParser, Parser, Serializer, object):
    """LoadSave

    Mixed-in with a store that implements add and visit and provides
    I/O for that class. Also, needs to be mixed in with something that
    provides parse_URI and output methods.
    """
    
    def __init__(self):
        super(LoadSave, self).__init__()
        self.uri = None
        self.location = None
        self.__lock = Lock()

    def generate_uri(self):
        """Return a new unique uri."""
        return URIRef(self.uri + path_generator.next())
    
    def load(self, location, uri=None, create=0):
        self.location = location        
        self.uri = URIRef(uri or location)

        scheme, netloc, path, params, query, fragment = urlparse(location)
        if create and netloc=="":
            import os
            # TODO: is this equiv to os.path.exists?            
            if not os.access(path, os.F_OK): 
                self.save(path, None)

        if self.location[-3:]==".nt":
            self.parse_nt_URI(location, self.uri)
        else:
            self.parse_URI(self.location, self.uri)

    def save(self, location=None, uri=None):
        print "In Save", location, uri
        try:
            self.__lock.acquire()
            location = location or self.location
            if not location:
                print "WARNING: not saving as no location has been set"
                return
            uri = uri or self.uri

            import tempfile, shutil, os
            name = tempfile.mktemp()            
            stream = open(name, 'wb')
            self.output(stream, uri)
            stream.close()

            if os.path.isfile(location):
                os.remove(location)
            shutil.copy(name, location)
            os.unlink(name)
        except Exception, e:
            from traceback import print_exc
            print_exc()
        finally:
            self.__lock.release()
        
