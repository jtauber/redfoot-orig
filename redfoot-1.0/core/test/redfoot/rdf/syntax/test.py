from os.path import dirname, join
import sys
test_dir = dirname(sys.modules[__name__].__file__)


from redfoot.rdf import syntax

print dir(syntax)

from redfoot.rdf.syntax import parser

class Test:

    def __init__(self):
        self.pass_count = 0
        self.fail_count = 0

        self.anonymous_count = 0
        self.anonymous_uri = {}

    def add_triple(self, s, p, o, anonymous_subject=0, literal_object=0, anonymous_object=0):
        if literal_object:
            o = "^" + o
        if anonymous_subject:
            if self.anonymous_uri.has_key(s):
                s = self.anonymous_uri[s]
            else:
                self.anonymous_count = self.anonymous_count + 1
                self.anonymous_uri[s] = "~" + str(self.anonymous_count)
                s = self.anonymous_uri[s]
        if anonymous_object:
            if self.anonymous_uri.has_key(o):
                o = self.anonymous_uri[o]
            else:
                self.anonymous_count = self.anonymous_count + 1
                self.anonymous_uri[o] = "~" + str(self.anonymous_count)
                o = self.anonymous_uri[o]
        self.model.append((s, p, o))

    def test_rdf(self, filename, test_model):
        self.model = []
        file = open(join(test_dir, filename))
        parser.parse(self.add_triple, file, "TODO: baseURI")
        if self.compare(self.model, test_model):
            print file,"PASSED"
            self.pass_count = self.pass_count + 1
        else:
            print file,"FAILED"
            self.fail_count = self.fail_count + 1

    def compare(self, model, test_model):
        for triple in model:
            if not triple in test_model:
                print "failed", triple
                return 0
        for triple in test_model:
            if not triple in model:
                print "failed", triple
                return 0
        return 1

    def test(self):
        # 2.2.1 Basic Serialization Syntax

        test_model = [("http://www.w3.org/Home/Lassila",
                      "http://description.org/schema/Creator",
                      "^Ora Lassila")]

        self.test_rdf("001.rdf", test_model)
        self.test_rdf("002.rdf", test_model)
        self.test_rdf("003.rdf", test_model)
        self.test_rdf("004.rdf", test_model)

        # 2.2.2 Basic Abbreviated Syntax

        self.test_rdf("005.rdf", test_model)

        test_model = [("http://www.w3.org","http://description.org/schema/Publisher","^World Wide Web Consortium"),
                      ("http://www.w3.org","http://description.org/schema/Title","^W3C Home Page"),
                      ("http://www.w3.org","http://description.org/schema/Date","^1998-10-03T02:27")]

        self.test_rdf("006.rdf", test_model)
        self.test_rdf("007.rdf", test_model)

        test_model = [("http://www.w3.org/Home/Lassila", "http://description.org/schema/Creator", "http://www.w3.org/staffId/85740"),
                      ("http://www.w3.org/staffId/85740", "foo/Name", "^Ora Lassila"),
                      ("http://www.w3.org/staffId/85740", "foo/Email", "^lassila@w3.org")]
        
        self.test_rdf("008.rdf", test_model)
        self.test_rdf("009.rdf", test_model)

        self.test_rdf("010.rdf", test_model)

        test_model = [("http://www.w3.org/staffId/85740", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "http://description.org/schema/Person"),
                      ("http://www.w3.org/staffId/85740", "foo/Name", "^Ora Lassila"),
                      ("http://www.w3.org/staffId/85740", "foo/Email", "^lassila@w3.org"),
                      ("http://www.w3.org/Home/Lassila", "http://description.org/schema/Creator", "http://www.w3.org/staffId/85740")]

        self.test_rdf("011.rdf", test_model)
        self.test_rdf("012.rdf", test_model)

        # 3.2 Container Syntax

        test_model = [('~1', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag'),
                      ('~1', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#_1', 'http://mycollege.edu/students/Amy'),
                      ('~1', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#_2', 'http://mycollege.edu/students/Tim'),
                      ('~1', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#_3', 'http://mycollege.edu/students/John'),
                      ('~1', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#_4', 'http://mycollege.edu/students/Mary'),
                      ('~1', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#_5', 'http://mycollege.edu/students/Sue'),
                      ('http://mycollege.edu/courses/6.001', 'http://description.org/schema/students', '~1')]

        self.test_rdf("013.rdf", test_model)

        test_model = [('~1', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Alt'),
                      ('~1', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#_1', 'ftp://ftp.x.org'),
                      ('~1', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#_2', 'ftp://ftp.cs.purdue.edu'),
                      ('~1', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#_3', 'ftp://ftp.eu.net'),
                      ('http://x.org/packages/X11', 'http://description.org/schema/DistributionSite', '~1')]
        
        self.test_rdf("014.rdf", test_model)

        # 3.3 Distribute Referents

        test_model = [('015.rdf#pages', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag'),
                      ('015.rdf#pages', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#_1', 'http://foo.org/foo.html'),
                      ('015.rdf#pages', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#_2', 'http://bar.org/bar.html'),
                      ('015.rdf#pages', 'http://description.org/schema/Creator', '^Ora Lassila')]

        self.test_rdf("015.rdf", test_model)

        print "%s passed; %s failed" % (self.pass_count, self.fail_count)
        
t = Test()
t.test()
