from redfootlib.rdf.nodes import URIRef

# Useful RDF constants

# SYNTAX
RDFNS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

TYPE = URIRef(RDFNS + "type")
PROPERTY = URIRef(RDFNS + "Property")
STATEMENT = URIRef(RDFNS + "Statement")
SUBJECT = URIRef(RDFNS + "subject")
PREDICATE = URIRef(RDFNS + "predicate")
OBJECT = URIRef(RDFNS + "object")

# SCHEMA
RDFSNS = "http://www.w3.org/2000/01/rdf-schema#"

CLASS = URIRef(RDFSNS + "Class")
RESOURCE = URIRef(RDFSNS + "Resource")
SUBCLASSOF = URIRef(RDFSNS + "subClassOf")
LABEL = URIRef(RDFSNS + "label")
COMMENT = URIRef(RDFSNS + "comment")
RANGE = URIRef(RDFSNS + "range")
DOMAIN = URIRef(RDFSNS + "domain")
LITERAL = URIRef(RDFSNS + "Literal")
CONTAINER = URIRef(RDFSNS + "Container")

