import sys
sys.path.extend(("../", "../../redfoot-core", "../../redfoot-components"))

from redfoot.rdf.query.functors import sort
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

    def print_link(self, s, p, o):
        label = self.label(s)
        sniffed_on = self.get_first_value(s, SNIFFED_ON, '??')
        sniffed_from = self.get_first_value(s, SNIFFED_FROM, '??')        
        print """\
%s:
  URI: %s
  SNIFFED_ON: %s
  SNIFFED_FROM: %s  
""" % (label, s, sniffed_on, sniffed_from)




sniffer = SnifferNode()
sniffer.load("link_sniffer.rdf", "http://eikeon.com", 1)
sniffer.run()

sniffer.do_prefix("sniff:<http://redfoot.net/2002/04/17/sniff/>")
sniffer.do_prefix("rdfs:<http://www.w3.org/2000/01/rdf-schema#>")
sniffer.do_prefix("rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>")

import threading
t = threading.Thread(target = sniffer.cmdloop, args = ())
t.setDaemon(0)
t.start()



####
from redfoot.server.module import App
from redfoot.rdf.objects import resource, literal
from redfoot.rdf.const import TYPE, LABEL, COMMENT
from link_sniffer import SNIFFED, SNIFFABLE, SNIFFED_ON, SNIFFED_FROM, RUN


class LinkApp(App):

    def display_link(self, request, response, s, p, o):
        rednode = self.rednode
        label = rednode.label(s)
        sniffed_on = rednode.get_first_value(s, SNIFFED_ON, '??')
        sniffed_from = rednode.get_first_value(s, SNIFFED_FROM, None)
        if sniffed_from:
            sniffed_from = rednode.label(sniffed_from)
        else:
            sniffed_from = "unknown"

        response.write("""\
    <p>
      <div><a href="%s">%s</a></div>
      <div class="small">%s</div>
      <div class="small">
        <span class="label">from:</span>&nbsp;%s <span class="label">on:</span>&nbsp;%s
      </div>      
    </p>""" % (s, label, s, sniffed_from, sniffed_on))
    
    def handle_request(self, request, response):
        start = int(request.get_parameter("start", "0"))
        end = int(request.get_parameter("end", "30"))
        sniffer = self.rednode
        response.write("""\
<!DOCTYPE html 
     PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
     "DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title>Link Sniffer</title>
    <style>
      body { 
        margin: 2% 4%; 
        background:  #FFF;
        color:       #000;
        font-family: "Trebuchet MS", sans-serif;
        font-size:   10pt;
      }
      a { 
        color: #000;
        text-decoration: underline; 
        font-weight: bold; 
      }
      a:hover {
        color: #333;
        text-decoration: underline; 
      }
      .small {
        font-size: 8pt;
      }
      .label {
	color: #999
      }
    </style>
  </head>
  <h1>Links</h1>
  <ul>
""")
        callback = lambda s, p, o: self.display_link(request, response, s, p, o)
        from functors import slice        
        sort(sniffer.reverse_chron, sniffer.visit)(slice(callback, start, end), (None, TYPE, SNIFFED))

        response.write("""\
  </ul>        
</html>
""");
        response.close()
    


from redfoot.server import RedServer

# Create a RedServer listening on address, port
server = RedServer('', 9090)

# Create an instance of AppClass to add to our RedServer
app = LinkApp(sniffer)
server.add_app(app)

# Run the App
#server.run() # blocks until server is shutdown

import threading
t = threading.Thread(target = server.run, args = ())
t.setDaemon(1)
t.start()
