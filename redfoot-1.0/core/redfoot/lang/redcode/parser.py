from xml.parsers.expat import ParserCreate

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

    parser.ParseFile(file)
        
    file.close()
    return documentHandler.module

