from redfoot.xml.handler import HandlerBase

import __builtin__

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


class ElementNode(Node):
    def __init__(self, name, atts):
        Node.__init__(self)
        self.name = name
        self.atts = atts

    def write(self, globals, locals):
        write = locals['_RF_write']
        name = self.name
        write("<%s" % name)
        atts = self.atts
        for key in atts.keys():
            write(''' %s="''' % key)
            atts[key].write(globals, locals)                         
            write('''"''')
        write(">")        
        self.children.write(globals, locals)
        write("</%s>" % name)        

                 
class TextNode(Node):
    def __init__(self, text):
        self.value = text

    def write(self, globals, locals):
        write = locals['_RF_write']
        write(self.value)


class EvalNode(Node):
    def __init__(self, code=None):
        self.code = code
    
    def write(self, globals, locals):
        result = __builtin__.eval(self.code, globals, locals)
        if result!=None:
            write = locals['_RF_write']
            if not hasattr(result, 'encode'):
                result = str(result)
            write(result)


class EncodedEvalNode(EvalNode):
    def __init__(self, code, encode):
        EvalNode.__init__(self, code)
        self.encode = encode
        
    def write(self, globals, locals):
        result = __builtin__.eval(self.code, globals, locals)
        if result!=None:
            write = locals['_RF_write']
            if not hasattr(result, 'encode'):
                result = str(result)
            write(self.encode(result))
                
