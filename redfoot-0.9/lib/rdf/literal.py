# $Header$

def literal(str):
    return u"^"+str

def is_literal(str):
    return str[0]==u"^"

def un_literal(str):
    return str[1:]

# $Log$
# Revision 5.1  2000/12/17 20:41:22  eikeon
# removed log message prior to currently worked on release
#
# Revision 5.0  2000/12/08 08:34:52  eikeon
# new release
