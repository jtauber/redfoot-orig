# $Header$

# SYNTAX
RDFNS = u"http://www.w3.org/1999/02/22-rdf-syntax-ns#"
TYPE = RDFNS+u"type"
PROPERTY = RDFNS+u"Property"
STATEMENT = RDFNS+u"Statement"
SUBJECT = RDFNS+u"subject"
PREDICATE = RDFNS+u"predicate"
OBJECT = RDFNS+u"object"

# SCHEMA
RDFSNS = u"http://www.w3.org/2000/01/rdf-schema#"
CLASS = RDFSNS+u"Class"
RESOURCE = RDFSNS+u"Resource"
SUBCLASSOF = RDFSNS+u"subClassOf"
LABEL = RDFSNS+u"label"
COMMENT = RDFSNS+u"comment"
RANGE = RDFSNS+u"range"
DOMAIN = RDFSNS+u"domain"
LITERAL = RDFSNS+u"Literal"

# $Log$
# Revision 5.2  2000/12/23 02:30:17  eikeon
# added warnings and test cases for when there is no RDF root element (or when there is more than one RDF element)
#
# Revision 5.1  2000/12/17 20:41:22  eikeon
# removed log message prior to currently worked on release
#
# Revision 5.0  2000/12/08 08:34:52  eikeon
# new release
