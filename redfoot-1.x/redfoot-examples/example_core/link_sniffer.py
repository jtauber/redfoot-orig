import sys
from time import sleep
from urlparse import urlparse, urlunparse, urljoin


from redfoot.rdf.store.urigen import generate_uri as get_timestamp
from redfoot.rdf.objects import resource, literal
from redfoot.rdf.const import TYPE, LABEL, COMMENT

SNIFFED = resource("http://redfoot.net/2002/04/17/sniff/ed")
SNIFFABLE = resource("http://redfoot.net/2002/04/17/sniff/able")
SNIFFED_ON = resource("http://redfoot.net/2002/04/17/sniff/date")
SNIFFED_FROM = resource("http://redfoot.net/2002/04/17/sniff/source")
RUN = resource("http://redfoot.net/2002/04/17/sniff/run")

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
        t = threading.Thread(target = self.__sniff, args = ())
        t.setDaemon(1)
        t.start()
        import threading
        t = threading.Thread(target = self.__timer, args = ())
        t.setDaemon(1)
        t.start()
        

    def __sniff(self):
        while 1:
            self.visit_by_type(s(self.sniff), SNIFFABLE, RUN, literal("1"))
            sleep(5)

    def __mark(self, subject):
        self.add(resource(subject), RUN, literal("1"))

    def __unmark(self, subject):
        self.remove(resource(subject), RUN, None)
        
    def __timer(self):
        while 1:
            sleep(60*60)
            self.visit(s(self.__mark), (None, TYPE, SNIFFABLE))


    def sniff(self, url):
        self.__unmark(url)        
        print "sniffing '%s'" % url
        sys.stdout.flush()
        from urllib import urlopen, quote

        f = urlopen(url)
        # TOD: refactor
        self.parser.sniffed_from = url        
        scheme, netloc, url, params, query, fragment = urlparse(url)
        self.parser.uri_base = "%s://%s" % (scheme, netloc)
        self.parser.feed(f.read())
        self.parser.close()
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

        
