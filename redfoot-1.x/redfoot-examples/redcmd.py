# redcmd.py

import dev_hack

from cmd import Cmd
from sys import exit
from redfoot.rdf.objects import resource, literal

def get_triple(text):
    subj_start = text.find("<", 0) + 1
    subj_end = text.find(">", subj_start)
    subject = resource(text[subj_start:subj_end])
    property_start = text.find("<", subj_end) + 1
    property_end = text.find(">", property_start)
    property = resource(text[property_start: property_end])
    value_start_if_literal = text.find('"', property_end) + 1
    if value_start_if_literal:
        value_start = value_start_if_literal
        value_end = text.rfind('"', value_start)
        value = literal(text[value_start:value_end])
    else:
        value_start = text.find("<", property_end) + 1
        value_end = text.find(">", value_start)
        value = resource(text[value_start:value_end])
    return (subject, property, value)

class RedCmd(object, Cmd):
    """
    Console for manipulating a Rednode
    """

    intro = "Redfoot Command Line"
    prompt = "RF>"

    def __init__(self):
        super(RedCmd, self).__init__()
        
    def do_quit(self, arg):
        """Quit the Redfoot Command Line"""
        print "Bye"
        exit(1)

    def do_add(self, arg):
        """add <subject> <predicate> (<object>|"object")"""
        s, p, o = get_triple(arg)
        self.add(s, p, o)
        print "added", s, p, o

    def do_remove(self, arg):
        """remove <subject> <predicate> (<object>|"object")"""
        s, p, o = get_triple(arg)
        self.remove(s, p, o)
        print "removed", s, p, o
        
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
        s, p, o = get_triple(arg)
        self.visit(print_triple, (s, p, o))

from redfoot.rdf.store.triple import TripleStore
    
class RedCmdStore(RedCmd, TripleStore): pass

red_cmd = RedCmdStore()
red_cmd.cmdloop()
