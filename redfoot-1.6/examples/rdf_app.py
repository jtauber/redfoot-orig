####
from redfootlib.server.module import App
from redfootlib.rdf.objects import resource, literal
from redfootlib.rdf.const import TYPE, LABEL, COMMENT

HTML = resource("http://redfoot.net/04/26/rapp/html")
OUTER_HTML = resource("http://redfoot.net/04/26/rapp/outer_html")
INNER_HTML = resource("http://redfoot.net/04/26/rapp/inner_html")
ALIAS_TO = resource("http://redfoot.net/04/26/rapp/alias_to")
CHAIN_TO = resource("http://redfoot.net/04/26/rapp/chain_to")

from rdf_app_parser import parse

class Processor(object):
    
    class State(object):
        __slots__ = ('consumed', 'remaining', 'next', 'followed', 'outer')
        def __init__(self, consumed='', remaining='', next=None):
            self.consumed = consumed
            self.remaining = remaining
            self.next = next
            self.followed = []
            self.outer = []
        def __repr__(self):
            return "(%s, %s, %s, %s)" % (self.consumed, self.remaining, self.next, self.followed)
    
    def __init__(self, rednode):
        self.rednode = rednode
        self.__states = []

    def get_state(self):
        return self.__states[-1]

    state = property(get_state)
    
    def handle_request(self, request, response):
        self.request = request
        self.response = response
        path = self.rednode.uri + request.get_path_info()[1:]
        initial = Processor.State('', path, self.exact)
        self.__states = [initial, ]

    def make_root(self):
        print "STATES:", self.__states
        self.__states = [self.__states[-1],]

    def stop(self):
        for check in self.state_iter():
            self.__states.pop()
    

    def __next(self):
        if self.__states:
            state = self.__states[-1]
            if state.next:
                return state.next
            else:
                self.__states.pop()
                return self.__next()
        else:
            return None
        
    def state_iter(self):
        return iter(self.__next, None)

    def exact(self):
        state = self.__states[-1]
        path = state.consumed + state.remaining
        html = self.rednode.neighbourhood.get_first_value(resource(path), HTML, None)
        if html:
            print "EXACT: %s" % path            
            self.response.write(html)
            self.__states.pop()
        else:
            state.next = self.alias

    def alias(self):
        state = self.__states[-1]
        path = state.consumed + state.remaining        

        class _Alias:
            def __init__(self):
                self.source = None
                self.longest = 0
            def __call__(self, source, p, destination):
                if len(source)>=len(state.consumed):
                    if path.find(source)==0:
                        if len(source)>self.longest:
                            self.longest = len(source)
                            self.source = source
                            self.destination = destination
                            self.type = p
        cb = _Alias()                            
        self.rednode.neighbourhood.visit(cb, (None, ALIAS_TO, None))
        self.rednode.neighbourhood.visit(cb, (None, CHAIN_TO, None))        

        if cb.source and not cb.source in state.followed:
            print "ALIAS: %s->%s" % (cb.source, cb.destination)            
            state.followed.append(cb.source)
            new_state = Processor.State()
            new_state.consumed = cb.destination
            new_state.remaining = path[len(cb.source):]
            new_state.next = self.exact
            new_state.followed = list(state.followed)
            if cb.type==ALIAS_TO:
                self.__states = [] # clear states
            self.__states.append(new_state)
        else:
            state.next = self.outer

    def outer(self):
        state = self.__states[-1]
        path = state.consumed + state.remaining
        l = []
        def _outer(subject, predicate, object):
            l.append(subject)
        self.rednode.neighbourhood.visit(_outer, (None, OUTER_HTML, None))
        
        l.sort(lambda a, b: len(a)-len(b))
        for o in l:
            if len(o)>=len(state.consumed) and o.find(state.consumed)==0:
                if path.find(o)==0 and not o in state.outer:
                    state.outer.append(o)
                    state.consumed = o
                    state.remaining = path[len(o):]
                    state.next = self.outer
                    print "OUTER:", o
                    data = self.rednode.neighbourhood.get_first_value(o, OUTER_HTML, None)
                    if data:
                        #state.next = self.inner
                        facet = self._parse(data, o)
                        if facet:
                            facet(self.rednode, self.request,
                                  self.response, self)
                            return
                        
        state.next = self.inner


    def inner(self):
        state = self.__states[-1]
        path = state.consumed + state.remaining
        html = self.rednode.neighbourhood.get_first_value(resource(path), INNER_HTML, None)
        if html:
            print "INNER: %s" % path            
            self.response.write(html)            
        self.__states.pop()

    def process(self):
        for check in self.state_iter():
            check()

    def _parse(self, codestr, facet_uri):
        locals = globals = {}
        try:
            parse(codestr, facet_uri, globals, locals)
        except:
            from traceback import print_exc
            print_exc()                
            def error(rednode, request, response, process):
                response.write("""
<h1>Error: Could not parse outer_html for '%s':</h1>
<pre>%s</pre>""" % (facet_uri, codestr))
            return error
        return globals.get(facet_uri, None)


class RDFApp(App):

    def __init__(self, rednode):
        super(RDFApp, self).__init__(rednode)
    
    def handle_request(self, request, response):
        processor = Processor(self.rednode)
        processor.handle_request(request, response)
        processor.process()
        response.close()

    
def n3style(o):
    if o.is_literal():
        return '"%s"' % o
    else:
        return '<%s>' % o
