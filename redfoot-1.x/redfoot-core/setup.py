#

from distutils.core import setup

setup(
    name = 'redfoot-core',
    version = "1.5.0",
    description = "A framework for building distributed data-driven web applications with RDF and Python",
    author = "Daniel 'eikeon' Krech, James Tauber ",
    author_email = "eikeon@eikeon.com, jtauber@jtauber.com",
    url = "http://redfoot.sourceforge.net/",

    packages = ['redfoot',
                'redfoot.rdf' ,
                'redfoot.rdf.query' ,'redfoot.rdf.store', 'redfoot.rdf.syntax',
                'redfoot.redcode',
                'redfoot.xml'],
    )


