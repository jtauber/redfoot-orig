def test_splitProperty():
    print splitProperty("foo#bar")
    print splitProperty("foo#3bar")
    print splitProperty("foo#3#bar")
    print splitProperty("http://www.test.com/foo")
    print splitProperty("http://www.test.com/foo#bar")
    print splitProperty("foo3bar") #TODO: should this return null namespace URI?
    print splitProperty("foobar") #TODO: should this return null namespace URI?
    print splitProperty("#bar")
    print splitProperty("bar#") #TODO: test fails (function should return None)
    print splitProperty("bar#3") #TODO: test fails (function should return None)

def testSerializer():
    s = Serializer()
    s.setBase("http://foo.com/")
    s.registerProperty("foo#author")
    s.start()
    s.subjectStart("http://jtauber.com")
    s.property("foo#author","^James Tauber")
    s.subjectEnd()
    s.end()
