from redfootlib.rdf.store.triple import TripleStore

from redfootlib.rdf.objects import resource, literal

from redfootlib.rdf.const import LABEL, RESOURCE
from redfootlib.rdf.const import TYPE, CLASS, SUBCLASSOF
from redfootlib.rdf.const import PROPERTY, DOMAIN, RANGE

from os.path import dirname, join, splitext
from os import listdir

MODULE = resource("http://redfoot.net/2002/05/20/module")
MODULE_CLASS = resource("http://redfoot.net/2002/05/20/Module")
# TODO: where to define the schema info? domain range etc

class ModuleStore(TripleStore):

    def __init__(self, namespace, directory):
        super(ModuleStore, self).__init__()
        self.namespace = namespace
        self.directory = directory
        self._load()
        self.add(MODULE_CLASS, TYPE, CLASS)
        self.add(MODULE_CLASS, SUBCLASSOF, RESOURCE)
        self.add(MODULE, TYPE, PROPERTY)
        self.add(MODULE, DOMAIN, RESOURCE)
        self.add(MODULE, RANGE, MODULE_CLASS)

    def _load(self):
        d = self.directory
        for file in listdir(d):
            if file[-3:]==".py" and not file=="__init__.py":
                uri = resource(self.namespace + splitext(file)[0])
                print uri
                f = open(join(d, file))
                module = f.read()
                self.add(uri, MODULE, literal(module))
                self.add(uri, TYPE, MODULE_CLASS)
