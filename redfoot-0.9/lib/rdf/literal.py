# $Header$

def literal(str):
    return u"^"+str

def is_literal(str):
    return str[0]==u"^"

def un_literal(str):
    return str[1:]

# $Log$
# Revision 6.1  2001/03/26 20:18:01  eikeon
# removed old log messages
#
# Revision 6.0  2001/02/19 05:01:23  jtauber
# new release
