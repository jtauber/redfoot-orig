from distutils.core import setup

setup(
    name = 'rdflib',
    version = "0.9.0",
    description = "RDF library containing an RDF triple store and RDF/XML parser/serializer",
    author = "Daniel 'eikeon' Krech, James Tauber ",
    author_email = "eikeon@eikeon.com, jtauber@jtauber.com",
    maintainer = "Daniel 'eikeon' Krech",
    maintainer_email = "eikeon@eikeon.com",
    url = "http://redfoot.sourceforge.net/",

    packages = ['rdflib',
                'rdflib.model',
                'rdflib.store',                
                'rdflib.syntax'],
    )

