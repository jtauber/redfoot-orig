from urlparse import urlparse        

from redfootlib.rdf.syntax.parser import Parser
from redfootlib.rdf.syntax.serializer import Serializer

from redfootlib.rdf.nodes import URIRef

from threading import Lock

class LoadSave(Parser, Serializer, object):
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


    def load(self, location, uri=None, create=0):
        self.location = location        
        self.uri = URIRef(uri or location)

        scheme, netloc, path, params, query, fragment = urlparse(location)
        if create and netloc=="":
            import os
            # TODO: is this equiv to os.path.exists?            
            if not os.access(path, os.F_OK): 
                self.save(path, None)
            
        self.parse_URI(self.location, self.uri)

    def save(self, location=None, uri=None):
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
        finally:
            self.__lock.release()
        
