from redfoot.rdf.store.objects import resource

from redfoot.rdf.syntax import parser, serializer

def print_triple(s, p, o, anonymous_subject=0, literal_object=0, anonymous_object=0):
    print s, p, o

#parser.parse_URI(print_triple, "xmlhack.rss")

print serializer.split_property("foo#bar")
print serializer.split_property("foo#3bar")
print serializer.split_property("foo#3#bar")
print serializer.split_property("http://www.test.com/foo")
print serializer.split_property("http://www.test.com/foo#bar")
print serializer.split_property("foo3bar")
print serializer.split_property("foobar")
print serializer.split_property("#bar")
print serializer.split_property("bar#")
print serializer.split_property("bar#3")

import sys
s = serializer.Serializer()
s.set_stream(sys.stdout)
s.register_property("b!ar")
s.start()
s.triple("foo", "b!ar", "baz")
s.triple("foo", "b!ar", "baz", literal_object=1)
s.end()




