# $Header$

def literal(str):
    return "^"+str

def is_literal(str):
    return str[0]=="^"

def un_literal(str):
    return str[1:]

# $Log$
# Revision 5.0  2000/12/08 08:34:52  eikeon
# new release
