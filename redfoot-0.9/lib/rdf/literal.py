# $Header$

def literal(str):
    return u"^"+str

def is_literal(str):
    return str[0]==u"^"

def un_literal(str):
    return str[1:]

# $Log$
# Revision 5.2  2000/12/23 02:30:17  eikeon
# added warnings and test cases for when there is no RDF root element (or when there is more than one RDF element)
#
# Revision 5.1  2000/12/17 20:41:22  eikeon
# removed log message prior to currently worked on release
#
# Revision 5.0  2000/12/08 08:34:52  eikeon
# new release
