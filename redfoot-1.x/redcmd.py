# redcmd.py

import dev_hack

from cmd import Cmd
from sys import exit
from redfootlib.rdf.objects import resource, literal


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

    def do_quit(self, arg):
        """Quit the Redfoot Command Line"""
        print "Bye"
        exit(1)

    def do_add(self, arg):
        """add <subject> <predicate> (<object>|"object")"""
        st = self.get_triple(arg)
        if st:
            self.add(st[0], st[1], st[2])
            print "added", st
        else:
            print "error"

    def do_remove(self, arg):
        """remove <subject> <predicate> (<object>|"object")"""
        st = self.get_triple(arg)
        if st:
            self.remove(st[0], st[1], st[2])
            print "removed", st
        else:
            print "error"
        
    def do_shell(self, arg):
        """! <python-statement>"""
        try:
            exec arg in globals(), globals()
        except Exception, e:
            print e

    def do_visit(self, arg):
        """visit <subject> <predicate> (<object>|"object")"""
        def print_triple(s, p, o):
            print s, p, o
        st = self.get_triple(arg)
        if st:
            self.visit(print_triple, st)
        else:
            print "error"

    def do_prefix(self, arg):
        """prefix p:<uri> or prefix :<uri>"""
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

from redfootlib.rdf.store.triple import TripleStore

class RedCmdStore(RedCmd, TripleStore): pass

if __name__ == "__main__":
    red_cmd = RedCmdStore()
    red_cmd.cmdloop()
