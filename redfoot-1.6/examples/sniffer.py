import sys
from time import sleep, time, gmtime, mktime
from urlparse import urlparse        

from redfootlib.rdf.objects import resource, literal
from redfootlib.rdf.const import TYPE, LABEL, COMMENT
from redfootlib.rdf.query.functors import s

from sniffer_html_parser import SnifferHTMLParser

SNIFFED = resource("http://redfoot.net/2002/04/17/sniff/ed")
SNIFFABLE = resource("http://redfoot.net/2002/04/17/sniff/able")
SNIFFED_FROM = resource("http://redfoot.net/2002/04/17/sniff/source")
# When a link was sniffed into the triple store
SNIFFED_ON = resource("http://redfoot.net/2002/04/17/sniff/date")

# When a resource was last sniffed for links
SNIFF_LAST = resource("http://redfoot.net/2002/04/17/sniff/last")

SNIFF_EVERY = resource("http://redfoot.net/2002/04/17/sniff/every")

SECONDS_IN_DAY = 60*60*24

from date_time import date_time, parse_date_time

class Sniffer(object):
    def __init__(self):
        super(Sniffer, self).__init__()
        self.ignore_list = ["www.google.com"]
                
    def run(self):
        import threading
        t = threading.Thread(target = self.__sniff, args = ())
        t.setDaemon(1)
        t.start()
        
    def __sniff(self):
        while 1:
            self.visit(s(self.__check), (None, TYPE, SNIFFABLE))
            sleep(5)

    def __check(self, url):
        every = int(self.get_first_value(url, SNIFF_EVERY, str(SECONDS_IN_DAY)))
        # TODO: take the oldest value
        last = self.get_first_value(url, SNIFF_LAST, None)
        if not last or time() - parse_date_time(last) > every:
            self.remove(url, SNIFF_LAST, None)
            self.add(url, SNIFF_LAST, literal(date_time()))
            self.sniff(url)
        
    def sniff(self, url):
        print "sniffing '%s'" % url
        sys.stdout.flush()
        adder = lambda href, label: self.add_sniffed(href, label, url)
        parser = SnifferHTMLParser(adder)
        parser.parse(url)
        print "Saving..."
        sys.stdout.flush()
        self.save()
        print "Done saving"

    def add_sniffed(self, href, label, sniffed_from):
        if not self.ignore(href):
            uri = resource(href)
            label = literal(label)
            if not self.exists(uri, None, None):
                print "ADDED:", href, label
                self.add(uri, LABEL, label)
                self.add(uri, TYPE, SNIFFED)
                timestamp = literal(date_time())
                self.add(uri, SNIFFED_ON, timestamp)
                self.add(uri, SNIFFED_FROM, resource(sniffed_from))
        

    def ignore(self, href):
        scheme, netloc, url, params, query, fragment = urlparse(href)
        return netloc in self.ignore_list
            

    # TODO: split into two comparators... reverse and chron
    def reverse_chron(self, (s1, p1, o1), (s2, p2, o2)):
        date_a = self.get_first_value(s1, SNIFFED_ON, '')
        date_b = self.get_first_value(s2, SNIFFED_ON, '')
        return 0-cmp(str(date_a), str(date_b))

        

from redfootlib.rdf.query.schema import SchemaQuery
from redfootlib.rdf.store.triple import TripleStore
from redfootlib.rdf.store.autosave import AutoSave
from redfootlib.rdf.store.storeio import LoadSave

class SnifferNode(Sniffer, SchemaQuery, AutoSave, LoadSave, TripleStore):
    """Default pre mixed Sniffer Node"""
    def __init__(self):
        super(SnifferNode, self).__init__()
        self.auto_save_min_interval = 60*60*12 # 12 hours
