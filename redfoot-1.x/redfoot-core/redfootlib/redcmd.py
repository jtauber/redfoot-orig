# redcmd.py

from cmd import Cmd
from sys import exit
from redfootlib.rdf.objects import resource, literal
from redfootlib.rednode import RedNode
from redfootlib.server import RedServer
from new import module

class RedCmd(object, Cmd):
    """
    Console for manipulating a Rednode
    """

    intro = "Redfoot Command Line"
    prompt = "RF>"

    def __init__(self):
        super(RedCmd, self).__init__()
        self.prefix_map = {}
        self.default_uri = None

        # Create a context for RedCmd exec(s)
        self.context = module("__redfoot__")

        # Create a RedNode        
        self.context.rednode = RedNode()

        self.context.server = None


    def __exec(self, code):
        locals = globals = self.context.__dict__
        try:
            exec code in globals, locals
        except:
            print "The following exception occured while trying to exec '%s'" % code
            from traceback import print_exc
            print_exc()
        
    def process_resource(self, text):
        if text == "ANY":
            r = None
        elif text[0] == "<" and text[-1] == ">":
            r = resource(text[1:-1])
        elif text.find(":") != -1:
            prefix, local_name = text.split(":")
            if prefix == "":
                if self.default_uri:
                    r = resource(self.default_uri + local_name)
                else:
                    return -1 # error
            elif prefix in self.prefix_map:
                r = resource(self.prefix_map[prefix] + local_name)
            else:
                return -1 # error
        else:
            return -1 # error
        return r
        
    def get_triple(self, text):
        parts = text.split(" ", 2)
        subject = self.process_resource(parts[0])
        if subject == -1:
            return None # error
        property = self.process_resource(parts[1])
        if property == -1:
            return None # error
        if parts[2][0] == '"' and parts[2][-1] == '"':
            value = literal(parts[2][1:-1])
        else:
            value = self.process_resource(parts[2])
            if value == -1:
                return None # error
        return (subject, property, value)

    def emptyline(self):
        # over ride not to repeat last command
        pass

    def default(self, line):
        if line and line[0]!="#":
            super(RedCmd, self).default(line)

    def do_quit(self, arg):
        """\
Quit the Redfoot Command Line

Quit, saving if possible.
"""
        print "Saving rednode..."
        rednode = self.context.rednode
        try:
            self.context.rednode.save()
        except:
            print "Got the following exception while trying to save:"
            from traceback import print_exc
            print_exc()
            
        print "done."
        print "Bye"
        exit(1)

    def do_add(self, arg):
        """\
add <subject> <predicate> (<object>|"object")

Add the triple.
Example:  add <http://redfoot.sourceforge.net/> rdfs:label "Redfoot homepage" where rdfs is first defined using the prefix command.
"""
        st = self.get_triple(arg)
        if st:
            self.context.rednode.add(st[0], st[1], st[2])
            print "added", st
        else:
            print "error: see 'help add'"

    def do_remove(self, arg):
        """remove <subject> <predicate> (<object>|"object")"""
        st = self.get_triple(arg)
        if st:
            self.context.rednode.remove(st[0], st[1], st[2])
            print "removed", st
        else:
            print "error"
        
    def do_shell(self, arg):
        """! <python-statement>"""
        try:
            self.__exec(arg)
        except Exception, e:
            print e

    def do_visit(self, arg):
        """\
visit <subject>|ANY <predicate>|ANY (<object>|"object"|ANY)

Examples:
  visit ANY ANY ANY  -- will visit all triples
  visit <http://eikeon.com/> ANY ANY -- will visit all triples with subject of http://eikeon.com/
"""
        def print_triple(s, p, o):
            print s, p, o
        st = self.get_triple(arg)
        if st:
            self.context.rednode.visit(print_triple, st)
        else:
            print "error"

    def do_prefix(self, arg):
        """\
prefix p:<uri> or prefix :<uri>

Examples:
  prefix rdf:http://www.w3.org/1999/02/22-rdf-syntax-ns#
  prefix rdfs:http://www.w3.org/TR/WD-rdf-schema#

  Then rdf:label can be used as an abbreviation for <http://www.w3.org/1999/02/22-rdf-syntax-ns#label>
"""
        prefix, uri_text = arg.split(":", 1)
        if uri_text[0] == "<" and uri_text[-1] == ">":
            uri = uri_text[1:-1]
            if prefix == "":
                self.default_uri = uri
                print "mapped default prefix to", uri
            else:
                self.prefix_map[prefix] = uri
                print "mapped prefix", prefix, "to", uri
        else:
            print "error"

    def do_load(self, arg):
        """\
load <location> <uri>

Load a new RDF file using uri as the base URI, creating the file if it does not exist."""

        print "loading",  arg
        # Load RDF data from location using uri as the base URI, creating a
        # file if one does not already exist.
        # @@@ do we need to make sure we only do this once?
        location, uri = arg.split()
            
        self.context.rednode.load(location, uri, 1)

    def do_server(self, arg):
        """\
server <address>:<port>

Start a server listening on address:port with no apps running on
it. Use add_app to add apps to the server. Currently it is recommended
that only one server be run."""

        if arg.find(":")==-1:
            print "usage: server <address>:<port>"
            return
        
        address, port = arg.split(":", 1)
        # Create a RedServer listening on address, port
        self.context.server = RedServer(address, int(port))
        self.context.server.run(background=1)

    def do_redcode(self, arg):
        """\
redcode on

Turn on redcode support so that app/modules written in redcode can
work. """

        # TODO: check arg and uninstall... for now install reguardless
        
        from redfootlib.redcode import importer
        importer.install()

    def do_add_app(self, arg):
        """\
add_app package_name.app_name

Adds app defined in package_name.app_name to previously running server. If a server has not yet been started then one is started on :9090"""
        
        parts = arg.split(" ")
        if not len(parts)==1:
            print "usage: add_app package_name.app_name"
            return
        names = parts[0].split(".")
        if len(names)==2:
            package, name = ".".join(names[:-1]), names[-1]
            locals = globals = self.context.__dict__            
            module = __import__(package, globals, locals)
            AppClass = eval(name, module.__dict__)            
        else:
            print "usage: add_app package_name.app_name"

        app = AppClass(self.context.rednode)

        if not self.context.server:
            self.context.server = RedServer('', 9090)
            self.context.server.run(background=1)                    

        self.context.server.add_app(app)

    
