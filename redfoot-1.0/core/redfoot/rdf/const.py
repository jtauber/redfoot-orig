from redfoot.rdf.objects import resource

# Useful RDF constants

# SYNTAX
RDFNS = u"http://www.w3.org/1999/02/22-rdf-syntax-ns#"

TYPE = resource(RDFNS + u"type")
PROPERTY = resource(RDFNS + u"Property")
STATEMENT = resource(RDFNS + u"Statement")
SUBJECT = resource(RDFNS + u"subject")
PREDICATE = resource(RDFNS + u"predicate")
OBJECT = resource(RDFNS + u"object")

# SCHEMA
RDFSNS = u"http://www.w3.org/2000/01/rdf-schema#"

CLASS = resource(RDFSNS + u"Class")
RESOURCE = resource(RDFSNS + u"Resource")
SUBCLASSOF = resource(RDFSNS + u"subClassOf")
LABEL = resource(RDFSNS + u"label")
COMMENT = resource(RDFSNS + u"comment")
RANGE = resource(RDFSNS + u"range")
DOMAIN = resource(RDFSNS + u"domain")
LITERAL = resource(RDFSNS + u"Literal")
CONTAINER = resource(RDFSNS + u"Container")

