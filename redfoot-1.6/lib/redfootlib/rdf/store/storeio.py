from urlparse import urlparse        

from redfootlib.rdf.syntax.parser import Parser
from redfootlib.rdf.syntax.serializer import RedSerializer

from threading import Lock

class LoadSave(Parser, RedSerializer, object):
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
        self.uri = uri or location

        scheme, netloc, path, params, query, fragment = urlparse(location)
        if create and netloc=="":
            import os
            # TODO: is this equiv to os.path.exists?            
            if not os.access(path, os.F_OK): 
                self.save(path, None)
            
        self.parse_URI(self.location, self.uri)

    def save(self, location=None, uri=None):
        self.__lock.acquire()
        location = location or self.location
        if not location:
            print "WARNING: not saving as no location has been set"
            return
        uri = uri or self.uri
        stream = open(location, 'wb')
        self.output(stream, uri)
        stream.close()
        self.__lock.release()
        
