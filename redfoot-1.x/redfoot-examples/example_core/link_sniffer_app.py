import sys
sys.path.extend(("../", "../../redfoot-core", "../../redfoot-components"))

from redfoot.rdf.query.schema import SchemaQuery
from redfoot.rdf.store.triple import TripleStore
from redfoot.rdf.store.autosave import AutoSave
from redfoot.rdf.store.storeio import LoadSave

from link_sniffer import Sniffer
from redcmd import RedCmd

class SnifferNode(RedCmd, Sniffer, SchemaQuery, LoadSave, TripleStore):
    ""

    def do_quit(self, arg):
        """Quit the Redfoot Command Line"""
        print "Saving RDF..."
        self.save()
        print "...Done"
        super(SnifferNode, self).do_quit(arg)


sniffer = SnifferNode()
sniffer.load("link_sniffer.rdf", "http://eikeon.com", 1)
sniffer.run()

sniffer.do_prefix("sniff:<http://redfoot.net/2002/04/17/sniff/>")
sniffer.do_prefix("rdfs:<http://www.w3.org/2000/01/rdf-schema#>")
sniffer.do_prefix("rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>")

#### Run LinkApp HTTP interface
from link_sniffer_http_app import run_app
run_app(sniffer) 

# Finally we run the cmdloop... which blocks until the user quits from
# cmd.
sniffer.cmdloop()
