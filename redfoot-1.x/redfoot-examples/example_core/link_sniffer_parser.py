from htmllib import HTMLParser
import formatter

from urlparse import urlparse, urlunparse, urljoin


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
    def __init__(self, adder):
        HTMLParser.__init__(self, formatter.NullFormatter(), 0)
        self.adder = adder

    def parse(self, url):
        scheme, netloc, path, params, query, fragment = urlparse(url)
        self.uri_base = "%s://%s" % (scheme, netloc)
        from urllib import urlopen, quote
        f = urlopen(url)
        self.feed(f.read())
        self.close()

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

            try:
                label = self.anchorText.encode('ascii')
            except:
                print "TODO: Am having encoding issues"
                label = 'TODO: encoding issue'

            self.adder(href, label)
                
            self.anchor = None
