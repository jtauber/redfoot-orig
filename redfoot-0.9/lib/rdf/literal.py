# $Header$

def literal(str):
    return u"^"+str

def is_literal(str):
    return str[0]==u"^"

def un_literal(str):
    return str[1:]

# $Log$
# Revision 7.0  2001/03/26 23:41:04  eikeon
# NEW RELEASE
