from ihooks import ModuleImporter, ModuleLoader, PY_SOURCE
from urllib2 import urlopen, HTTPError
from urlparse import urljoin

import re, tempfile, shutil, os

pattern = re.compile(r"^(https?://[^ ]+)")
url_path = ["http://eikeon.com/2002/06/16/", "http://eikeon.com/2002/06/15/"]

class HTTPModuleLoader(ModuleLoader):

    def find_module(self, name, path = None):
        stuff = ModuleLoader.find_module(self, name, path)
        if stuff:
            return stuff
        if path:
            return
        
        if self.verbose: print "looking for: ", name, path            
        for base in url_path:
            url = urljoin(base, name + ".py")
            try:
                file = urlopen(url)
                name = tempfile.mktemp()            
                stream = open(name, 'wb')
                stream.write(file.read())
                stream.close
                file = open(name, 'r')
                return file, url, ('.py', 'r', 1)
            except HTTPError, he:
                print "Did not find: ", url
                print he
        return None


class HTTPModuleImporter(ModuleImporter):
    def __init__(self):
        hooks, verbose = (None, 1)
        loader = HTTPModuleLoader(hooks, verbose)
        ModuleImporter.__init__(self, loader, verbose)


HTTPModuleImporter().install()

