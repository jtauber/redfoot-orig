# $Header$

def literal(str):
    return "^"+str

def is_literal(str):
    return str[0]=="^"

def un_literal(str):
    return str[1:]

# $Log$
# Revision 1.1  2000/12/03 22:23:13  jtauber
# created literal.py for literal handling
#
