from xml.parsers.expat import ParserCreate
from xml.parsers import expat
from xml.parsers.expat import ExpatError

from exceptions import SyntaxError

def parse(source, name, handler_class):
    if hasattr(source, 'read'):
        return _parse(source, name, handler_class)
    else:
        # assume source is a location
        f = open(source, 'r')
        module = _parse(f)
        module.__file__ = source
        return module

def _parse(file, name, handler_class):
    parser = ParserCreate(namespace_separator="^")
    parser.returns_unicode = 1
    
    documentHandler = handler_class(parser, name)

    try:
        parser.ParseFile(file)
    except ExpatError, msg:
        errno = parser.ErrorCode
        if errno>0:
            raise SyntaxError, u"Error at line:%s, column: %s, " % (parser.ErrorLineNumber, parser.ErrorColumnNumber) + "%s\n" % expat.ErrorString(errno)        
        
    file.close()
    return documentHandler.module

