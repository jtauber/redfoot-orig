import sys
from time import sleep
from urlparse import urlparse        

from redfootlib.rdf.store.urigen import generate_uri as get_timestamp
from redfootlib.rdf.objects import resource, literal
from redfootlib.rdf.const import TYPE, LABEL, COMMENT
from redfootlib.rdf.query.functors import s

from sniffer_html_parser import SnifferHTMLParser

SNIFFED = resource("http://redfoot.net/2002/04/17/sniff/ed")
SNIFFABLE = resource("http://redfoot.net/2002/04/17/sniff/able")
SNIFFED_ON = resource("http://redfoot.net/2002/04/17/sniff/date")
SNIFFED_FROM = resource("http://redfoot.net/2002/04/17/sniff/source")
RUN = resource("http://redfoot.net/2002/04/17/sniff/run")


class Sniffer(object):
    def __init__(self):
        super(Sniffer, self).__init__()
        self.ignore_list = ["www.google.com"]
                
    def run(self):
        import threading
        t = threading.Thread(target = self.__sniff, args = ())
        t.setDaemon(1)
        t.start()
        import threading
        t = threading.Thread(target = self.__timer, args = ())
        t.setDaemon(1)
        t.start()
        
    def add_sniffed(self, href, label, sniffed_from):
        if not self.ignore(href):
            uri = resource(href)
            label = literal(label)
            if not self.exists(uri, None, None):
                print "ADDED:", href, label
                self.add(uri, LABEL, label)
                self.add(uri, TYPE, SNIFFED)
                timestamp = literal(get_timestamp())
                self.add(uri, SNIFFED_ON, timestamp)
                self.add(uri, SNIFFED_FROM, resource(sniffed_from))
        

    def __sniff(self):
        while 1:
            self.visit_by_type(s(self.sniff), SNIFFABLE, RUN, literal("1"))
            sleep(5)

    def __mark(self, subject):
        self.add(resource(subject), RUN, literal("1"))

    def __unmark(self, subject):
        self.remove(resource(subject), RUN, None)
        
    def mark(self, subject=None):
        self.visit(s(self.__mark), (None, TYPE, SNIFFABLE))        

    def __timer(self):
        while 1:
            self.mark(None)
            sleep(60*30)            


    def sniff(self, url):
        self.__unmark(url)        
        print "sniffing '%s'" % url
        sys.stdout.flush()
        adder = lambda href, label: self.add_sniffed(href, label, url)
        parser = SnifferHTMLParser(adder)
        parser.parse(url)
        print "Saving..."
        sys.stdout.flush()
        self.save()
        print "Done saving"
        

    def ignore(self, href):
        scheme, netloc, url, params, query, fragment = urlparse(href)
        return netloc in self.ignore_list
            

    # TODO: split into two comparators... reverse and chron
    def reverse_chron(self, (s1, p1, o1), (s2, p2, o2)):
        date_a = self.get_first_value(s1, SNIFFED_ON, '')
        date_b = self.get_first_value(s2, SNIFFED_ON, '')
        return 0-cmp(str(date_a), str(date_b))

        
