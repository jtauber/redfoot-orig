import sys
sys.path.extend(("../../redfoot-core", "../../redfoot-components"))


from time import sleep
from urlparse import urlparse, urlunparse, urljoin


from functors import slice

from redfoot.rdf.store.urigen import generate_uri as get_timestamp
from redfoot.rdf.objects import resource, literal
from redfoot.rdf.const import TYPE, LABEL, COMMENT

SNIFFED = resource("http://eikeon.com/2002/03/27/sniffed-1")
SNIFFABLE = resource("http://redfoot.net/04/17/sniffable")
SNIFFED_ON = resource("http://redfoot.net/2002/04/17/sniffer/sniffed_on")
SNIFFED_FROM = resource("http://redfoot.net/2002/04/17/sniffer/sniffed_from")

from htmllib import HTMLParser
import formatter

hostname_cache = {}
import socket
def get_hostname(host):
    hostname = hostname_cache.get(host, None)
    if not hostname:
        try:
            hostname = socket.gethostbyaddr(host)[0]
        except socket.error:
            hostname = host
        hostname_cache[host] = hostname            
    return hostname

class SnifferHTMLParser(HTMLParser):
    def __init__(self, store):
        HTMLParser.__init__(self, formatter.NullFormatter(), 0)
        self.store = store

    def anchor_bgn(self, href, name, type):
        self.save_bgn()        
        self.anchor = href

    def anchor_end(self):
        if self.anchor:
            href=self.anchor
            self.anchorText = self.save_end()
            scheme, netloc, url, params, query, fragment = urlparse(href)

            if netloc=="":
                href = urljoin(self.uri_base, href)
            else:
                netloc = get_hostname(netloc)
                href = urlunparse((scheme, netloc, url, params, query, fragment))

            if not self.store.ignore(href):
                uri = resource(href)
                if not self.store.exists(uri, None, None):
                    print "ADDED:", href, self.anchorText
                    try:
                        label = literal(self.anchorText.encode('ascii'))
                    except:
                        print "TODO: Am having encoding issues"
                        label = literal('TODO: encoding issue')
                    self.store.add(uri, LABEL, label)
                    self.store.add(uri, TYPE, SNIFFED)
                    timestamp = literal(get_timestamp())
                    self.store.add(uri, SNIFFED_ON, timestamp)
                    self.store.add(uri, SNIFFED_FROM, resource(self.sniffed_from))
                
            self.anchor = None
        

from redfoot.rdf.query.functors import s

class Sniffer(object):
    def __init__(self):
        super(Sniffer, self).__init__()
        self.parser = SnifferHTMLParser(self)
        self.ignore_list = ["www.google.com"]
                
    def run(self):
        import threading
        t = threading.Thread(target = self.__run, args = ())
        t.setDaemon(1)
        t.start()
        

    def __run(self):
        while 1:
            # TODO: change to keep running once every n hours
            print "Sniffing for new links..."
            sys.stdout.flush()            
            self.visit(s(self.sniff), (None, TYPE, SNIFFABLE))
            print "Done sniffing for new links"
            sys.stdout.flush()
            # TODO: check that store has a save
            print "Saving..."
            sys.stdout.flush()
            self.save()
            print "Done saving"
            sys.stdout.flush()            
            sleep(60*15)

    def sniff(self, url):
        from urllib import urlopen, quote

        f = urlopen(url)
        # TOD: refactor
        self.parser.sniffed_from = url        
        scheme, netloc, url, params, query, fragment = urlparse(url)
        self.parser.uri_base = "%s://%s" % (scheme, netloc)
        self.parser.feed(f.read())
        self.parser.close()

    def ignore(self, href):
        scheme, netloc, url, params, query, fragment = urlparse(href)
        return netloc in self.ignore_list
            

    # TODO: split into two comparators... reverse and chron
    def reverse_chron(self, (s1, p1, o1), (s2, p2, o2)):
        date_a = self.get_first_value(s1, SNIFFED_ON, '')
        date_b = self.get_first_value(s2, SNIFFED_ON, '')
        return 0-cmp(str(date_a), str(date_b))

        
#from redfoot.rednode import RedNode
from redfoot.rdf.query.schema import SchemaQuery
from redfoot.rdf.store.triple import TripleStore
from redfoot.rdf.store.autosave import AutoSave
from redfoot.rdf.store.storeio import LoadSave


class SnifferNode(Sniffer, SchemaQuery, LoadSave, TripleStore):
    ""

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

from redfoot.rdf.query.functors import sort

#sniffer.add(resource("http://rdfig.xmlhack.com/index.html"), TYPE, SNIFFABLE)
#sites = [] # ["http://freshmeat.net/"]
#for site in sites:
#    sniffer.add(resource(site), TYPE, SNIFFABLE)    
#sort(sniffer.reverse_chron, sniffer.visit)(slice(sniffer.print_link, 0, 30), (None, TYPE, SNIFFED))

sniffer.run()



####
from redfoot.server.module import App

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
server.run() # blocks until server is shutdown
