import pyexpat

# TODO shouldn't be hardcoded -jkt
#execfile(r"D:\home\projects\cvs-work\redfoot\parser\rdfparser.py")
from rdf.parser import *

def add(subject, predicate, object):
    #print u"%s\n" % object
    print "object: '"
    print object.encode('UTF-8')
    print "'\n"
    #print u"%s\n" % object
    #print u"s : %s\np : %s\no : %s\n" % (object, object, object)
    #print u"s : %s\np : %s\no : %s\n" % (subject, predicate, object)
    #print u"s : %s\np : %s\no : %s\n" % (subject, predicate, object)
    #print u"s : %s\np : %s\no : %s\n" % (subject.encode('UTF-8'), subject.encode('UTF-8'), subject.encode('UTF-8'))
    #print (subject, predicate, object)

def test(rdf):
    parser = pyexpat.ParserCreate(namespace_separator="")
    RootHandler(parser, add, None)
    parser.Parse(rdf)
    print dir(parser)
    print "asdf"

def testFile(filename, baseURI=None):
    parser = pyexpat.ParserCreate(namespace_separator="")
    if baseURI!=None:
        parser.SetBase(baseURI)
    RootHandler(parser, None)
    f = open(filename)
    parser.ParseFile(f)
    f.close()

#testFile(r"D:\home\projects\cvs-work\redfoot\rdfSyntax.rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns")
#testFile(r"D:\home\projects\cvs-work\redfoot\rdfSchema.rdf","http://www.w3.org/2000/01/rdf-schema")
#testFile(r"D:\home\projects\cvs-work\redfoot\redfoot-builtin.rdf","http://xteam.hq.bowstreet.com/redfoot-builtin")

def test_1():
    print "\nTEST ONE"
    test("""<?xml version="1.0"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="http://description.org/schema/">
      <rdf:Description about="http://www.w3.org/Home/Lassila">
        <s:Creator>Ora Lassila</s:Creator>
      </rdf:Description>
    </rdf:RDF>""")

def test_2():
    print "\nTEST TWO"
    test("""<?xml version="1.0"?>
    <RDF xmlns="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <Description about="http://www.w3.org/Home/Lassila">
        <Creator xmlns="http://description.org/schema/">Ora Lassila</Creator>
      </Description>
    </RDF>""")

def test_3():
    print "\nTEST THREE"
    test("""<?xml version="1.0"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="http://description.org/schema/">
      <rdf:Description about="http://www.w3.org/Home/Lassila"
                       s:Creator="Ora Lassila" />
    </rdf:RDF>""")

def test_4():
    print "\nTEST FOUR"
    test("""<?xml version="1.0"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="http://description.org/schema/">
      <rdf:Description about="http://www.w3.org">
        <s:Publisher>World Wide Web Consortium</s:Publisher>
        <s:Title>W3C Home Page</s:Title>
        <s:Date>1998-10-03T02:27</s:Date>
      </rdf:Description>
    </rdf:RDF>""")

def test_5():
    print "\nTEST FIVE"
    test("""<?xml version="1.0"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="http://description.org/schema/">
      <rdf:Description about="http://www.w3.org"
           s:Publisher="World Wide Web Consortium"
           s:Title="W3C Home Page"
           s:Date="1998-10-03T02:27"/>
    </rdf:RDF>""")

def test_6():
    print "\nTEST SIX"
    test("""<?xml version="1.0"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="s#"
      xmlns:v="v#">
      <rdf:Description about="http://www.w3.org/Home/Lassila">
        <s:Creator rdf:resource="http://www.w3.org/staffId/85740"/>
      </rdf:Description>

      <rdf:Description about="http://www.w3.org/staffId/85740">
        <v:Name>Ora Lassila</v:Name>
        <v:Email>lassila@w3.org</v:Email>
      </rdf:Description>
    </rdf:RDF>""")

def test_7():
    print "\nTEST SEVEN"
    test("""<?xml version="1.0"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="s#"
      xmlns:v="v#">
      <rdf:Description about="http://www.w3.org/Home/Lassila">
        <s:Creator>
          <rdf:Description about="http://www.w3.org/staffId/85740">
            <v:Name>Ora Lassila</v:Name>
            <v:Email>lassila@w3.org</v:Email>
          </rdf:Description>
        </s:Creator>
      </rdf:Description>
    </rdf:RDF>""")

def test_8():
    print "\nTEST EIGHT"
    test("""<?xml version="1.0"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="s#"
      xmlns:v="v#">
  <rdf:Description about="http://www.w3.org/Home/Lassila">
    <s:Creator rdf:resource="http://www.w3.org/staffId/85740"
       v:Name="Ora Lassila"
       v:Email="lassila@w3.org" />
  </rdf:Description>
</rdf:RDF>""")


# THIS ONE CAUSES A FAULT IN PYTHON 2.0b1 ON WINDOWS 2000
def test_9():
    print "\nTEST NINE"
    test("""<?xml version="1.0"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="s#"
      xmlns:v="v#">
        <s:foo about="http://www.w3.org/Home/Lassila">
          <s:Creator>bar</s:Creator>
        </s:foo>
    </rdf:RDF>""")

# THIS SEEMS TO BE A BUG IN THE SPEC
# HOW IS AN RDF PROCESSOR TO KNOW THAT <s:Person>...</s:Person> is a Description?
def test_10():
    print "\nTEST TEN"

    test("""<?xml version="1.0"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="s#"
      xmlns:v="v#">
  <rdf:Description about="http://www.w3.org/Home/Lassila">
    <s:Creator>
      <s:Person about="http://www.w3.org/staffId/85740">
	<v:Name>Ora Lassila</v:Name>
	<v:Email>lassila@w3.org</v:Email>
      </s:Person>
    </s:Creator>
  </rdf:Description>
</rdf:RDF>""")

def test_11():
    print "\nTEST ELEVEN"

    test("""<?xml version="1.0"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="s#"
      xmlns:v="v#">
  <rdf:Description about="http://mycollege.edu/courses/6.001">
    <s:students>
      <rdf:Bag>
	<rdf:li resource="http://mycollege.edu/students/Amy"/>
	<rdf:li resource="http://mycollege.edu/students/Tim"/>
	<rdf:li resource="http://mycollege.edu/students/John"/>
	<rdf:li resource="http://mycollege.edu/students/Mary"/>
	<rdf:li resource="http://mycollege.edu/students/Sue"/>
      </rdf:Bag>
    </s:students>
  </rdf:Description>
</rdf:RDF>""")

def test_no_root():
    print "\nTEST NO ROOT"
    test("""<?xml version="1.0"?>
    <tmp>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#WRONG-NAMESPACE"
      xmlns:s="http://description.org/schema/">
      <rdf:Description about="http://www.w3.org/Home/Lassila">
        <s:Creator>Ora Lassila</s:Creator>
      </rdf:Description>
    </rdf:RDF>
    <b/>
    </tmp>
    """)

def test_two_roots():
    print "\nTEST TWO ROOTS"
    test("""<?xml version="1.0"?>
    <two>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="http://description.org/schema/">
      <rdf:Description about="http://www.w3.org/Home/Lassila">
        <s:Creator>Ora Lassila</s:Creator>
      </rdf:Description>
    </rdf:RDF>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="http://description.org/schema/">
      <rdf:Description about="http://www.w3.org/Home/Lassila">
        <s:Creator>Ora Lassila</s:Creator>
      </rdf:Description>
    </rdf:RDF>
    </two>
""")

def test_encoding():
    print "\nTEST ENCODING"
    test("""<?xml version="1.0"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="http://description.org/schema/">
      <rdf:Description about="http://www.w3.org/Home/Lassila">
        <s:Creator>Ora Lassila©</s:Creator>
      </rdf:Description>
    </rdf:RDF>
""")

def test_encoding2():
    print "\nTEST ENCODING"
    test("""<?xml version="1.0" encoding="iso-8859-1"?>
    <rdf:RDF
      xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:s="http://description.org/schema/">
      <rdf:Description about="http://www.w3.org/Home/Lassila">
        <s:Creator>Ora Lassila©</s:Creator>
      </rdf:Description>
    </rdf:RDF>
""")

#test_1()
#test_no_root()
#test_two_roots()
#test_encoding()

from urllib import urlopen

def testing():
    parser = pyexpat.ParserCreate(encoding='UTF-8', namespace_separator="")
    RootHandler(parser, add, None)
    #f = urlopen('zh-utf8-8.xml')
    f = urlopen('test.xml')
    parser.ParseFile(f)
    f.close()

testing()
