#

# install_redcode_module_importer
from redfoot.redcode.importer import RedcodeModuleImporter

from redfoot.module import App

__modules = {}
__apps_dict = {} 
__apps = [] # ordered list of apps

def register_app(uri, app_class):
    __apps_dict[uri] = app_class        
    __apps.append((uri, app_class))

def register_module(uri, app_class):
    if issubclass(app_class, App):
        register_app(uri, app_class)
    else:
        __modules[uri] = app_class

def get_module(uri):
    return __modules.get(uri, None)

def get_app(uri):
    return __apps_dict.get(uri, None)

def get_apps():
    return list(__apps)
