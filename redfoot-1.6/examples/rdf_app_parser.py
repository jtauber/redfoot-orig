from xml.parsers.expat import ParserCreate

from redfootlib.xml.handler import HandlerBase
from redfootlib.rdf.objects import resource, literal

from exceptions import SyntaxError, Exception

FACET = resource("http://redfoot.net/04/26/rapp/^facet")
APPLY = resource("http://redfoot.net/04/26/rapp/^apply")
EXEC = resource("http://redfoot.net/04/26/rapp/^exec")

class HTMLHandler(HandlerBase, object):

    def __init__(self, parser):
        HandlerBase.__init__(self, parser, None)
        self.data = ''
        args = "rednode, request, response, processor"
        self.codestr = '''\
def _tmp(%s):
'''  % args

    def child(self, name, atts):
        if name==FACET:
            pass
        elif name==APPLY:
            if self.data:
                self.codestr = self.codestr + '''\
        response.write("""%s""")
''' % self.data
                self.data = ''
            self.codestr = self.codestr + '''\
        processor.process()
'''                
        elif name==EXEC:
            self.eh = Exec(self.parser, self)
        else:
            if len(atts)==0:
                self.data = self.data + "<%s>" % name
            else:
                self.data = self.data + "<%s " % name
                for item in atts.iteritems():
                    self.data = self.data + '%s="%s"' % item
                self.data = self.data +">"

    def char(self, data):
        self.data = self.data + data

    def execstr(self, codestr):
        if self.data:        
            self.codestr = self.codestr + '''\
        response.write("""%s""")
''' % self.data
            self.data = ''
        for line in codestr.split("\n"):
            self.codestr = self.codestr + '''\
        %s
''' % line        

    def end(self, name):        
        if name!=APPLY and name!=FACET:
            self.data = self.data + "</%s>" % name

    def get_codestr(self):
        if self.data:
            self.codestr = self.codestr + '''\
        response.write("""%s""")
''' % self.data
            self.data = ''
        return self.codestr



def parse(data, facet_uri, globals, locals):
    parser = ParserCreate(namespace_separator="^")
    parser.returns_unicode = 0
    
    htmlHandler = HTMLHandler(parser)
    parser.Parse(data)

    codestr = htmlHandler.get_codestr()
    try:
        exec codestr+"\n" in globals, locals
        globals[facet_uri] = locals['_tmp']
        del locals['_tmp']
    except Exception, e:
        from traceback import print_exc
        print_exc()                
        print e, codestr
    return


from redfootlib.server.redcode.handlers import adjust_indent


class Exec(HandlerBase, object):

    def __init__(self, parser, parent):
        HandlerBase.__init__(self, parser, parent,)
        self.data = ""
        
    def child(self, name, atts):
        if len(atts)==0:
            self.data = self.data + "<%s>" % name
        else:
            self.data = self.data + "<%s " % name
            for item in atts.iteritems():
                self.data = self.data + '%s="%s"' % item
            self.data = self.data +">"
        
    
    def char(self, data):
        self.data = self.data + data

    def end(self, name):
        if name==EXEC:
            super(Exec, self).end(name)        
            self.parent.execstr(adjust_indent(self.data))
        else:
            self.data = self.data + "</%s>" % name
