#

# install_redcode_module_importer
from redfoot.redcode.importer import RedcodeModuleImporter

modules = {}

def register_app(uri, app_class):
    modules[uri] = app_class

