
import poplib, rfc822, string

from redfootlib.rdf.store.triple import TripleStore
from redfootlib.rdf.objects import resource, literal
from redfootlib.rdf.const import TYPE

POP_URI = "http://redfoot.sourceforge.net/2001/08/POP/"
RFC_822_URI = "http://redfoot.sourceforge.net/2001/08/RFC822/"

MESSAGE = resource(POP_URI+"Message")
SUBJECT = resource(RFC_822_URI+"subject")
FROM = resource(RFC_822_URI+"from")
DATE = resource(RFC_822_URI+"date")
BODY = resource(POP_URI+"BODY")

class POP_Connector:

    def __init__(self, host, username, password):
        self.store = TripleStore()
        M = poplib.POP3(host)
        M.user(username)
        M.pass_(password)
        numMessages = len(M.list()[1])
        self.messages = {}
        for i in range(numMessages):
            uidl = string.split(M.uidl(i+1))[2]
            msg = M.retr(i+1)[1]
            lineFile = LineFile(msg)
            message = rfc822.Message(lineFile)
            bodyStartLine = lineFile.count
            headers = message.dict
            body = string.join(msg[bodyStartLine:], "\n")

            subject = resource(POP_URI + uidl)
            for header in headers.keys():
                predicate = resource(RFC_822_URI + header)
                object = literal(headers[header])
                self.store.add(subject, predicate, object)
            self.store.add(subject, BODY, literal(body))
            self.store.add(subject, TYPE, MESSAGE)
        M.quit()
        
    def visit(self, callback, triple):
        return self.store.visit(callback, triple)

class LineFile:
    """makes a list of lines look like a file"""

    def __init__(self, lines):
        self.lines = lines
        self.length = len(self.lines)
        self.count = 0

    def readline(self):
        self.count = self.count + 1
        if self.count > self.length:
            return None
        else:
            return self.lines[self.count]+"\n"
