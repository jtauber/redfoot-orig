import new
from string import find, split, join, strip, lstrip, whitespace

from redfoot.xml.handler import HandlerBase

from redfoot.xml.dom import Node, NodeList, TextNode
from redfoot.xml.dom import ElementNode, EvalNode, EncodedEvalNode

from redfoot.util import encode_attribute_value, encode_character_data

from exceptions import SyntaxError
from exceptions import Exception

# TODO change names
NS = "http://redfoot.sourceforge.net/2001/06/^"
CODE = NS+"code" 
MODULE = NS+"module"
APP = NS+"app"
FACET = NS+"facet"
SUB_MODULE = NS+"sub-module"

EVAL = NS+"eval"
EXEC = NS+"exec"
VISIT = NS+"visit"
CALLBACK = NS+"callback"
APPLY = NS+"apply"
IF = NS+"if"
FOR = NS+"for"
ELSE = NS+"else"
ELSEIF = NS+"elif"


import __builtin__

def parse_attribute(str):
    open = find(str, '{')
    if open>=0:
        close = find(str, '}', open) 
        if close>=0:
            nl = NodeList()
            nl.add(TextNode(encode_attribute_value(str[0:open])))

            val = str[open+1:close]
            code = __builtin__.compile(val, val, "eval")
            
            nl.add(EncodedEvalNode(code, encode_attribute_value))
            nl.add(parse_attribute(str[close+1:]))
            return nl
                   
    return TextNode(encode_attribute_value(str))


def adjust_indent(orig):
    lines = split(orig, "\n")
    indent = None
    str = ''
    for line in lines:
        if not indent:
            if lstrip(line)!='':
                indent = ''
                for c in line:
                    if c in whitespace:
                        indent = indent + c
                    else:
                        break
                if indent=='':
                    return orig
                str = str + line[len(indent):] + "\n"                    
        else:
            if find(line, indent)!=0:
                if not strip(line)=='':
                    print "Did not find expected indent at line '%s' in '%s'" % (line, orig)
            else:
                str = str + line[len(indent):] + "\n"
    return str
    



class ElementHandler(HandlerBase):
    def __init__(self, parser, parent, name, atts):
        HandlerBase.__init__(self, parser, parent)
        self.locals = parent.locals
        self.globals = parent.globals
        self.module = parent.module
        e_atts = {}
        for key in atts.keys():
            e_atts[key] = parse_attribute(atts[key])
        self.element = ElementNode(name, e_atts)
        
    def child(self, name, atts):
        if name==EVAL:
            h = Eval(self.parser, self)
        elif name==EXEC:
            h = Exec(self.parser, self)
        elif name==VISIT:
            h = Visit(self.parser, self, name, atts)
        elif name==APPLY:
            h = Apply(self.parser, self, atts.get('search', None)) 
        elif name==IF:
            h = If(self.parser, self, name, atts)
        elif name==FOR:
            h = For(self.parser, self, name, atts)
        else:
            h = ElementHandler(self.parser, self, name, atts)
        self.element.children.add(h.element)
    
    def char(self, data):
#          for c in data:
#              if not c in whitespace:
#                  self.element.add(TextNode(data))
#                  return
        self.element.add(TextNode(data))


class RedcodeRootHandler(HandlerBase):

    def __init__(self, parser, name):
        HandlerBase.__init__(self, parser, None)
        self.name = name

    def child(self, name, atts):
        if name==CODE:
            module_name = self.name
            rfch = CodeHandler(self.parser, self, module_name)
            self.module = rfch.module            
        else:
            msg = "Expected a '%s' root element but found '%s'" % (CODE, name)
            raise SyntaxError, msg

    def end(self, name):
        # override HandlerBase
        pass


class RedCodeException(Exception):
    def __init__(self, tag, exception, codestr, module):
        self.tag = tag
        self.exception = exception
        self.codestr = codestr
        self.module = module

    def __str__(self):
        return """
    Where:
      %s (in %s tag)
    What:
      %s: %s

    Context:
%s
""" % (self.module.__name__, self.tag, self.exception.__class__.__name__, str(self.exception), self.codestr)


class CodeHandler(HandlerBase):

    def __init__(self, parser, parent, name):
        HandlerBase.__init__(self, parser, parent)
        self.module = new.module(name)
        self.globals = self.module.__dict__
        self.locals = self.globals
        self.codestr = ""

    def _exec(self, codestr):
        try:
            exec codestr+"\n" in self.globals, self.locals
        except Exception, e:
            raise RedCodeException(CODE, e, codestr, self.module)

    def child(self, name, atts):
        codestr = adjust_indent(self.codestr)
        if codestr!="":
            self._exec(codestr)
            self.codestr = ""
        if name==MODULE:
            if atts.has_key('bases'):
                bases = "(" + atts['bases'] + ",)"
                base_classes = eval(bases, self.globals, self.locals)
            else:
                base_classes = (__import__('redfoot.module', self.globals, self.locals, ['ParentModule']).ParentModule, )
            eh = ModuleHandler(self.parser, self, atts['name'], base_classes)
        elif name==APP:
            base_classes = (__import__('redfoot.module', self.globals, self.locals, ['App']).App, )
            eh = ModuleHandler(self.parser, self, atts['name'], base_classes)
            
        else:
            raise SyntaxError, "\n" + str("\n\nUnexpeced element '%s'\n" % name)

    def char(self, data):
        self.codestr = self.codestr + data

    def end(self, name):
        HandlerBase.end(self, name)
        self._exec(adjust_indent(self.codestr)+"\n")


class ModuleHandler(HandlerBase):

    def __init__(self, parser, parent, name, base_classes):
        HandlerBase.__init__(self, parser, parent)
        self.locals = {}
        self.locals['RF_sub_modules'] = []
        self.globals = self.parent.locals
        self.codestr = ""
        self.name = name
        self.module = parent.module
        self.base_classes = base_classes
            
    def _exec(self, codestr):
        try:
            exec codestr+"\n" in self.globals, self.locals
        except Exception, e:
            raise RedCodeException(CODE, e, codestr, self.module)
        

    def child(self, name, atts):
        if name==FACET:
            nh = Facet(self.parser, self, atts['name'], atts)
            self.locals[atts['name'].encode('ascii')] = self.locals['_RF_facet']
        elif name==SUB_MODULE:
            SubModule(self.parser, self, atts)
        else:
            raise SyntaxError, "Unexpected Element: '%s'\n" % name

    def char(self, data):
        self.codestr = self.codestr + data

    def end(self, name):
        HandlerBase.end(self, name)
        self._exec(adjust_indent(self.codestr)+"\n")
        classobj = new.classobj(self.name.encode('ascii'), self.base_classes, self.locals )
        module = self.module
        classobj.__module__ = module.__name__
        module.__dict__[classobj.__name__] = classobj
        module.__dict__['_RF_APP'] = classobj


class SubModule(HandlerBase):
    def __init__(self, parser, parent, atts):
        HandlerBase.__init__(self, parser, parent)
        if not atts.has_key('instance'):
            msg = "sub-module is missing required instance attribute"
            raise SyntaxError, msg
        instance_name = atts['instance']
        if not atts.has_key('class'):
            msg = "sub-module is missing required class attribute"
            raise SyntaxError, msg
        class_name = atts['class']
        from_str = atts.get('from', None)
        if from_str:
            self.module = self.parent.module
            self.globals = self.module.__dict__
            self.locals = self.globals
            self._exec("from %s import %s" % (from_str, class_name))
        parent.locals['RF_sub_modules'].append((instance_name, class_name))


    def _exec(self, codestr):
        try:
            exec codestr+"\n" in self.globals, self.locals
        except Exception, e:
            raise RedCodeException(SUB_MODULE, e, codestr, self.module)


    def child(self, name, atts):
        msg = "No children allowed. Found '%s'" % name
        raise SyntaxError, msg
        


class If(ElementHandler):
    def __init__(self, parser, parent, name, atts):
        HandlerBase.__init__(self, parser, parent)
        self.locals = parent.locals
        self.globals = parent.globals
        self.module = parent.module
        test = atts['test']
        self.element = IfNodeList(test)

    def child(self, name, atts):
        if name==ELSEIF:
            h = ElementHandler(self.parser, self, name, atts)                    
            self.element.add_clause(atts['test'], h.element.children)
        elif name==ELSE:
            h = ElementHandler(self.parser, self, name, atts)                    
            self.element.add_clause("1", h.element.children)
        else:
            ElementHandler.child(self, name, atts)


class IfNodeList(Node):
    def __init__(self, test):
        Node.__init__(self)
        self.clauses = []        
        self.add_clause(test, self.children)

    def add_clause(self, test, nodelist):
        self.clauses.append((test, nodelist))
        
    def write(self, globals, locals):
        for clause in self.clauses:
            if __builtin__.eval(clause[0], globals, locals):
                clause[1].write(globals, locals)
                break


class For(ElementHandler):
    def __init__(self, parser, parent, name, atts):
        HandlerBase.__init__(self, parser, parent)
        self.locals = self.parent.locals
        self.globals = self.parent.globals
        self.module = parent.module        
        item = atts['item']
        list = atts['list']
        code = __builtin__.compile(list, list, "eval")                
        self.element = ForNodeList(item, code)


class ForNodeList(Node):
    def __init__(self, item, list):
        Node.__init__(self)
        self.item = item
        self.list = list

    def write(self, globals, locals):
        for item in __builtin__.eval(self.list, globals, locals):
            locals[self.item] = item
            self.children.write(globals, locals)


class Facet(ElementHandler):
    def __init__(self, parser, parent, name, atts):
        ElementHandler.__init__(self, parser, parent, name, atts)
        if atts.has_key('args'):
            args = "self, %s" % join(split(atts['args'], ","),",")
        else:
            args = "self"
        args = args + ", _RF_node=_RF_node"
        
        self.locals['_RF_node'] = self.element.children

        codestr = """\
def _RF_facet(%s):
    _RF_write = self.app.response.write
    _RF_node.write(globals(), locals())
""" % args

        self._exec(codestr)

    def _exec(self, codestr):
        try:
            exec codestr+"\n" in self.globals, self.locals
        except Exception, e:
            raise RedCodeException(FACET, e, codestr, self.module)
        

class VisitNode(Node):
    def write(self, globals, locals):
        from new import instancemethod
        locals['_RF_callback'] = instancemethod(self.callback, locals['self'], Node)
        __builtin__.eval(self.code, globals, locals)


class Visit(ElementHandler):
    def __init__(self, parser, parent, name, atts):
        ElementHandler.__init__(self, parser, parent, name, atts)
        self.element = VisitNode()        
        self.first_child = 1
        if atts.has_key('match'):
            args = atts['match']
        elif atts.has_key('args'):
            args = atts['args']
        else:
            args = "(None, None, None)"
            
        codestr = "%s(_RF_callback, %s)" % (atts.get('visit', 'self.app.rednode.visit'), args)
        code = __builtin__.compile(codestr, codestr, "eval")
        self.element.code = code

    def _exec(self, codestr):
        try:
            exec codestr+"\n" in self.globals, self.locals
        except Exception, e:
            raise RedCodeException(VISIT, e, codestr, self.module)

    def child(self, name, atts):
        if self.first_child:
            self.first_child = 0
            
            if name==CALLBACK:
                nh = Facet(self.parser, self, "ANON", atts)
                self.element.callback = self.locals['_RF_facet']
            else:
                self.locals['_RF_node'] = self.element.children                
                codestr = """\
def _RF_facet(self, subject, property, object, _RF_node=_RF_node):
    _RF_write = self.app.response.write
    _RF_node.write(globals(), locals())
"""
                self._exec(codestr)
                self.element.callback = self.locals['_RF_facet']
                ElementHandler.child(self, name, atts)         
        else:
            ElementHandler.child(self, name, atts)


class Eval(HandlerBase):

    def __init__(self, parser, parent):
        HandlerBase.__init__(self, parser, parent)
        self.locals = self.parent.locals
        self.globals = self.parent.globals
        self.codestr = ""
        # TODO: add supoprt for EvalNode without Encoding?
        self.element = EncodedEvalNode(None, encode_character_data)
        
    def child(self, name, atts):
        msg = "No children allowed. Found '%s'" % name
        raise SyntaxError, msg
    
    
    def char(self, data):
        self.codestr = self.codestr + data

    def end(self, name):
        HandlerBase.end(self, name)
        self.codestr = adjust_indent(self.codestr)
        code = __builtin__.compile(self.codestr, self.codestr, self.kind())
        self.element.code = code

    def kind(self):
        return "eval"


class Exec(Eval):
    def __init__(self, parser, parent):
        Eval.__init__(self, parser, parent)
        
    def kind(self):
        return "exec"


class Apply(HandlerBase):
    def __init__(self, parser, parent, modules):
        HandlerBase.__init__(self, parser, parent)
        self.locals = self.parent.locals
        self.globals = self.parent.globals
        self.modules = modules
        self.element = EvalNode()
        
    def child(self, name, atts):
        msg = "No children allowed. Found '%s'" % name
        raise SyntaxError, msg
    
    def end(self, name):
        HandlerBase.end(self, name)
        self.codestr = "self.apply("
        if self.modules:
            self.codestr = self.codestr + "modules=(%s,), " % self.modules
        self.codestr = self.codestr + ")"
        code = __builtin__.compile(self.codestr, self.codestr, 'exec')
        self.element.code = code

    def kind(self):
        return "eval"



