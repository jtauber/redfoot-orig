# $Header$

import new
import sys
import string
import __builtin__
        
RF_NS = u"http://redfoot.sourceforge.net/2001/01/^"
RF_CLASS = RF_NS+u"class"
RF_MODULE = RF_NS+u"module"
RF_EXEC = RF_NS+u"exec"
RF_CALL = RF_NS+u"call"
RF_EVAL = RF_NS+u"eval"
RF_RESPONSE = RF_NS+u"response"

RF_IF = RF_NS+u"if"
RF_ELSEIF = RF_NS+u"elseif"
RF_ELSE = RF_NS+u"else"

RF_FOR = RF_NS+u"for"

def encodeURI(s):
    return string.join(string.split(s,'#'),u'%23')

def encode_attribute(s):
    return string.join(string.split(s,'"'),u'&quot;')

def parse_red_page(location):
    import pyexpat
    parser = pyexpat.ParserCreate(namespace_separator="^")

    #parser.SetBase(baseURI)
    rfch = Root_Handler(parser, None)

    parser.returns_unicode = 1
    f = open(location, 'r')

    parser.ParseFile(f)
    errno = parser.ErrorCode
    if errno>0:
        sys.stderr.write(u"Error parsing file at line '%s' and column '%s',\n" % (parser.ErrorLineNumber, parser.ErrorColumnNumber) )
        sys.stderr.write("%s\n" % pyexpat.ErrorString(errno))        
        sys.stderr.flush()
        
    f.close()
    module = rfch.module
    module.__file__ = location
    return rfch.module


class HandlerBase:
    def __init__(self, parser, parent):
        self.parser = parser
        self.parent = parent
        self.set_handlers()

    def set_handlers(self):
        self.parser.StartElementHandler = self.child
        self.parser.CharacterDataHandler = self.char
        self.parser.EndElementHandler = self.end

    def char(self, data):
        pass

    def child(self, name, atts):
        pass
    
    def end(self, name):
        self.parent.set_handlers()


class IgnoreHandler(HandlerBase):
    def child(self, name, atts):
        print "Ignoring '%s'" % name
        IgnoreHandler(self.parser, self.adder, self)


class Root_Handler(HandlerBase):
    def __init__(self, parser, parent):
        HandlerBase.__init__(self, parser, parent)

    def child(self, name, atts):
        if name==RF_MODULE:
            if atts.has_key('name'):
                module_name = atts['name']
            else:
                raise "Module does not have required name attribute"
            rfch = RF_MODULE_Handler(self.parser, self, module_name)
            self.module = rfch.module            
        else:
            sys.stderr.write("did not find a '%s' root element... instead found '%s'" % (RF_MODULE, name))
            sys.stderr.flush()

    def end(self, name):
        pass
        # root has no parent
        #HandlerBase.end(self, name)


class RF_MODULE_Handler(HandlerBase):
    def __init__(self, parser, parent, name):
        HandlerBase.__init__(self, parser, parent)
        self.module = new.module(name)
        self.globals = self.module.__dict__
        self.locals = self.globals
        self.codestr = ""
    def child(self, name, atts):
        codestr = self.codestr
        if codestr!="":
            exec codestr+"\n" in self.globals, self.locals
            self.codestr = ""
        if name==RF_CLASS:
            if atts.has_key('bases'):
                import string
                bases = "(" + string.join(string.split(atts['bases']),",") + ",)"
                base_classes = __builtin__.eval(bases, self.globals, self.locals)
            else:
                base_classes = ()
            eh = RF_CLASS_Handler(self.parser, self, atts['name'], base_classes)
            classobj = eh.classobj
            module = self.module
            classobj.__module__ = module.__name__
            module.__dict__[classobj.__name__] = classobj
        else:
            sys.stderr.write("Ignoring '%s'\n" % name)
            sys.stderr.flush()

    def char(self, data):
        self.codestr = self.codestr + data

    def end(self, name):
        HandlerBase.end(self, name)
        exec self.codestr+"\n" in self.globals, self.locals


class RF_CLASS_Handler(HandlerBase):
    def __init__(self, parser, parent, name, base_classes):
        HandlerBase.__init__(self, parser, parent)

        #self.locals = self.parent.locals
        self.classobj = new.classobj(name.encode('ascii'), base_classes, {})
        self.locals = self.classobj.__dict__
        self.globals = self.parent.locals
        self.codestr = ""
            
    def child(self, name, atts):
        if name==RF_RESPONSE:
            nh = RF_RESPONSE_Handler(self.parser, self, atts['name'], atts)
        else:
            sys.stderr.write("Ignoring '%s'\n" % name)
            sys.stderr.flush()

    def char(self, data):
        self.codestr = self.codestr + data

    def end(self, name):
        HandlerBase.end(self, name)
        exec self.codestr+"\n" in self.globals, self.locals

class RF_PROCESSOR_Handler(HandlerBase):
    def __init__(self, parser, parent, name, base_classes):
        HandlerBase.__init__(self, parser, parent)

        #self.locals = self.parent.locals
        self.classobj = new.classobj(name.encode('ascii'), base_classes, {})
        self.locals = self.classobj.__dict__
        self.globals = self.parent.locals
        self.codestr = ""
            
    def child(self, name, atts):
        if name==RF_RESPONSE:
            nh = RF_RESPONSE_Handler(self.parser, self, atts['name'], atts)
        else:
            sys.stderr.write("Ignoring '%s'\n" % name)
            sys.stderr.flush()

    def char(self, data):
        self.codestr = self.codestr + data

    def end(self, name):
        HandlerBase.end(self, name)
        exec self.codestr+"\n" in self.globals, self.locals


class RF_EVAL_Handler(HandlerBase):
    def __init__(self, parser, parent):
        HandlerBase.__init__(self, parser, parent)
        self.locals = self.parent.locals
        self.globals = self.parent.globals
        self.codestr = u""
        self.element = EvalNode()
        
    def child(self, name, atts):
        raise "No children allowed"
    
    def char(self, data):
        self.codestr = self.codestr + data

    def end(self, name):
        HandlerBase.end(self, name)
        #code = __builtin__.compile(self.codestr, "<string>", self.kind())
        code = __builtin__.compile(self.codestr, self.codestr, self.kind())
        self.element.code = code

    def kind(self):
        return "eval"

class RF_EXEC_Handler(RF_EVAL_Handler):
    def __init__(self, parser, parent):
        RF_EVAL_Handler.__init__(self, parser, parent)
        
    def kind(self):
        return "exec"


class RF_CALL_Handler(HandlerBase):
    def __init__(self, parser, parent):
        HandlerBase.__init__(self, parser, parent)
        self.locals = self.parent.locals
        self.globals = self.parent.globals
        self.codestr = u""
        self.element = EvalNode()

        
        
    def child(self, name, atts):
        IgnoreHandler(self.parser, self)
    
    def char(self, data):
        self.codestr = self.codestr + data

    def end(self, name):
        HandlerBase.end(self, name)
        self.codestr = "apply(getattr(self, '%s'), (request, response))" % self.func_name.encode('ascii')
        #code = __builtin__.compile(self.codestr, "<string>", self.kind())
        code = __builtin__.compile(self.codestr, self.codestr, self.kind())
        self.element.code = code

    def kind(self):
        return "exec"


def parse_attribute(str):
    open = string.find(str, '{')
    if open>=0:
        close = string.find(str, '}', open) 
        if close>=0:
            nl = NodeList()
            nl.add(TextNode(encode_attribute(str[0:open])))

            #code = __builtin__.compile(str[open+1:close], "<string>", "eval")
            code = __builtin__.compile(str[open+1:close], str[open+1:close], "eval")
            
            nl.add(URIEncodedEvalNode(code))
            nl.add(parse_attribute(str[close+1:]))
            return nl
                   
    return TextNode(str)


class RF_Element(HandlerBase):
    def __init__(self, parser, parent, name, atts):
        HandlerBase.__init__(self, parser, parent)
        self.locals = self.parent.locals
        self.globals = self.parent.globals
        e_atts = {}
        for key in atts.keys():
            e_atts[key] = parse_attribute(atts[key])
        self.element = ElementNode(name, e_atts)
        
    def child(self, name, atts):
        if name==RF_EVAL:
            h = RF_EVAL_Handler(self.parser, self)
        elif name==RF_EXEC:
            h = RF_EXEC_Handler(self.parser, self)
        elif name==RF_CALL: # TODO: move to RF_RESPONSE
            h = RF_CALL_Handler(self.parser, self)
            h.func_name = atts['name']
        elif name==RF_IF:
            h = RF_If_Handler(self.parser, self, name, atts)
        elif name==RF_FOR:
            h = RF_For_Handler(self.parser, self, name, atts)
        else:
            h = RF_Element(self.parser, self, name, atts)
        self.element.children.add(h.element)
    
    def char(self, data):
#        for c in data:
#            if not c in string.whitespace:
#                self.element.add(TextNode(data))
#                return
        self.element.add(TextNode(data))

class RF_If_Handler(RF_Element):
    def __init__(self, parser, parent, name, atts):
        HandlerBase.__init__(self, parser, parent)
        self.locals = self.parent.locals
        self.globals = self.parent.globals
        test = atts['test']
        self.element = IfNodeList(test)

    def child(self, name, atts):
        if name==RF_ELSEIF:
            h = RF_Element(self.parser, self, name, atts)                    
            self.element.add_clause(atts['test'], h.element.children)
        elif name==RF_ELSE:
            h = RF_Element(self.parser, self, name, atts)                    
            self.element.add_clause("1", h.element.children)
        else:
            RF_Element.child(self, name, atts)

class RF_For_Handler(RF_Element):
    def __init__(self, parser, parent, name, atts):
        HandlerBase.__init__(self, parser, parent)
        self.locals = self.parent.locals
        self.globals = self.parent.globals
        item = atts['item']
        list = atts['list']
        #code = __builtin__.compile(list, "<string>", "eval")
        code = __builtin__.compile(list, list, "eval")                
        self.element = ForNodeList(item, code)
        

class RF_RESPONSE_Handler(RF_Element):
    def __init__(self, parser, parent, name, atts):
        RF_Element.__init__(self, parser, parent, name, atts)
        self.name = name
        if not self.globals.has_key('__nodes__'):
            self.globals['__nodes__'] = {}
        self.globals['__nodes__'][name] = self.element.children

        args = "request, response"
        if atts.has_key('args'):
            args = args + ", %s" % string.join(string.split(atts['args']),",")
        
        codestr = """\
def __tmp__(self, %s):
    __nodes__['%s'].write(globals(), locals())""" % (args, self.name) + "\n\n"
        exec codestr in self.globals, self.locals
        self.locals[self.name.encode('ascii')] = self.locals['__tmp__']
        


class Node:
    def __init__(self):
        self.children = NodeList()
        
    def add(self, child):
        self.children.add(child)

    def write(self, globals, locals):
        self.children.write(globals, locals)


class NodeList:
    def __init__(self):
        self.list = []

    def add(self, node):
        self.list.append(node)

    def write(self, globals, locals):
        for node in self.list:
            node.write(globals, locals)

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

class ForNodeList(Node):
    def __init__(self, item, list):
        Node.__init__(self)
        self.item = item
        self.list = list

    def write(self, globals, locals):
        for item in __builtin__.eval(self.list, globals, locals):
            locals[self.item] = item
            self.children.write(globals, locals)


class ElementNode(Node):
    def __init__(self, name, atts):
        Node.__init__(self)
        self.name = name
        self.atts = atts

    def write(self, globals, locals):
        writer = locals['response']
        name = self.name
        writer.write("<%s" % name)
        atts = self.atts
        for key in atts.keys():
            writer.write(''' %s="''' % key)
            atts[key].write(globals, locals)                         
            writer.write('''"''')
        writer.write(">")        
        self.children.write(globals, locals)
        writer.write("</%s>" % name)        

                 
class TextNode(Node):
    def __init__(self, text):
        self.value = text

    def write(self, globals, locals):
        locals['response'].write(self.value)


class EvalNode(Node):
    def __init__(self, code=None):
        self.code = code
    
    def write(self, globals, locals):
        result = __builtin__.eval(self.code, globals, locals)
        if result!=None:
            locals['response'].write(str(result))


# TODO: should wrap EvalNode with a URIEncoded writer instead?
class URIEncodedEvalNode(EvalNode):
    def write(self, globals, locals):
        locals['response'].write(encode_attribute(str(__builtin__.eval(self.code, globals, locals))))
        


#~ $Log$
#~ Revision 8.1  2001/04/27 02:47:15  eikeon
#~ added a namespace_separator character to be 'more' correct
#~
#~ Revision 8.0  2001/04/27 00:52:13  eikeon
#~ new release
