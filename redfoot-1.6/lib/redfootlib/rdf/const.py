from redfootlib.rdf.objects import resource

# Useful RDF constants

# SYNTAX
RDFNS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

TYPE = resource(RDFNS + "type")
PROPERTY = resource(RDFNS + "Property")
STATEMENT = resource(RDFNS + "Statement")
SUBJECT = resource(RDFNS + "subject")
PREDICATE = resource(RDFNS + "predicate")
OBJECT = resource(RDFNS + "object")

# SCHEMA
RDFSNS = "http://www.w3.org/2000/01/rdf-schema#"

CLASS = resource(RDFSNS + "Class")
RESOURCE = resource(RDFSNS + "Resource")
SUBCLASSOF = resource(RDFSNS + "subClassOf")
LABEL = resource(RDFSNS + "label")
COMMENT = resource(RDFSNS + "comment")
RANGE = resource(RDFSNS + "range")
DOMAIN = resource(RDFSNS + "domain")
LITERAL = resource(RDFSNS + "Literal")
CONTAINER = resource(RDFSNS + "Container")

