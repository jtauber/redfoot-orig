#
from redfoot.rdf.store.storeio import LoadSave
from redfoot.rdf.store.triple import TripleStore

class Store(LoadSave, TripleStore):
    def __init__(self):
        super(Store, self).__init__()


# TODO this belongs elsewhere (make generic first)
def to_relative_URL(path):
    import sys
    from os.path import join, dirname
    from urllib import pathname2url
    libDir = dirname(sys.modules["redfoot.rdf_files"].__file__)
    return pathname2url(join(libDir, path))


schema = Store()
schema.load(to_relative_URL("rdfSchema.rdf"), "http://www.w3.org/2000/01/rdf-schema")

syntax = Store()
syntax.load(to_relative_URL("rdfSyntax.rdf"), "http://www.w3.org/1999/02/22-rdf-syntax-ns")

builtin = Store()
builtin.load(to_relative_URL("builtin.rdf"), "http://redfoot.sourceforge.net/2000/10/06/builtin")





