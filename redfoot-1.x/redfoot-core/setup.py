#

from distutils.core import setup

from distutils.dist import Distribution
from distutils.command.build import build
from distutils.command.build_py import build_py

import os
from glob import glob
from types import *

class build_py_rdf(build_py):

    def find_package_modules (self, package, package_dir):
        self.check_package(package, package_dir)
        module_files = glob(os.path.join(package_dir, "*.py")) + glob(os.path.join(package_dir, "*.rdf"))
        modules = []
        setup_script = os.path.abspath(self.distribution.script_name)

        for f in module_files:
            abs_f = os.path.abspath(f)
            if abs_f != setup_script:
                module = os.path.splitext(os.path.basename(f))[0]
                modules.append((package, module, f))
            else:
                self.debug_print("excluding %s" % setup_script)
        return modules

    def build_module (self, module, module_file, package):
        if type(package) is StringType:
            package = package.split('.')
        elif type(package) not in (ListType, TupleType):
            raise TypeError, \
                  "'package' must be a string (dot-separated), list, or tuple"

        # Now put the module source file into the "build" area -- this is
        # easy, we just copy it somewhere under self.build_lib (the build
        # directory for Python source).
        outfile = self.get_module_outfile(self.build_lib, package, module)
        if  module_file.endswith(".rdf"): #XXX: hack for redcode modules
            outfile = outfile[0:outfile.rfind('.')] + ".rdf"
        dir = os.path.dirname(outfile)
        self.mkpath(dir)
        return self.copy_file(module_file, outfile, preserve_mode=0)


class RDFDistribution(Distribution):
    def get_command_class (self, command):
        if command=="build_py":
            self.cmdclass[command] = build_py_rdf
            return build_py_rdf
        else:
            return Distribution.get_command_class(self, command)

setup(
    distclass=RDFDistribution,    
    name = 'redfoot-core',
    version = "1.5.0",
    description = "A framework for building distributed data-driven web applications with RDF and Python",
    author = "Daniel 'eikeon' Krech, James Tauber ",
    author_email = "eikeon@eikeon.com, jtauber@jtauber.com",
    url = "http://redfoot.sourceforge.net/",

    packages = ['redfoot',
                'redfoot.rdf' ,
                'redfoot.rdf_files' ,                
                'redfoot.rdf.query' ,'redfoot.rdf.store', 'redfoot.rdf.syntax',
                'redfoot.redcode',
                'redfoot.server',
                'redfoot.xml'],
    )


