import dev_hack

from redfootlib.rdf.objects import resource, literal
from redfootlib.rdf.const import TYPE, LABEL, COMMENT
from redfootlib.rdf.const import STATEMENT, SUBJECT, PREDICATE, OBJECT

from redfootlib.rdf.query.functors import sort

from date_time import date_time
import time

from dailychumpbot import DailyChumpBot
from dailychump import DailyChump, Churn, ChurnEntry
from EntityEncoder import EntityEncoder        

CHUMP_ITEM = resource("http://redfoot.net/2002/05/13/chump/item")
CHUMP_TIME = resource("http://redfoot.net/2002/05/13/chump/time")
CHUMP_WHO = resource("http://redfoot.net/2002/05/13/chump/who")
CHUMP_COMMENT = resource("http://redfoot.net/2002/05/13/chump/comment")
CHUMP_KEYWORDS = resource("http://redfoot.net/2002/05/13/chump/keywords")


class RedChump(DailyChump):
    def __init__(self, archiver):
        self.archiver = archiver
        self.churn = self.archiver.retrieve_churn()


class RedChurn(Churn):        
    def __init__(self, store, make_statement, retract_statement):
        self.store = store
        self.make_statement = make_statement
        self.retract_statement = retract_statement
        self.database = {}
        self.labelcount = 0
        self.set_update_time(time.time())
        self.topic=""
        self.update()

    def add_item(self, item, nick, savenow=1):
        for label, entry in self.database.items():
            if item==entry.item:
                self.update_timestamp()                    
                return label
        
        entry = RedChurnEntry(item, self)            
        self.make_statement(resource(item), TYPE, CHUMP_ITEM)
        entry.set_time(time.time())            
        entry.set_nick(nick)
        label = self.get_next_label()
        self.set_entry(label, entry)
        self.save()

        return label
        
    def update(self):
        def _chump_item(s, p, o):
            entry = RedChurnEntry(s, self)
            label = self.get_next_label()
            self.set_entry(label, entry)
        def reverse_chron((s1, p1, o1), (s2, p2, o2)):
            date_a = self.store.get_first_value(s1, CHUMP_TIME, '')
            date_b = self.store.get_first_value(s2, CHUMP_TIME, '')
            return 0-cmp(str(date_a), str(date_b))
        sort(reverse_chron, self.store.visit)(_chump_item, (None, TYPE, CHUMP_ITEM)) 

    def save(self, location=None, uri=None):
        pass


class RedChurnEntry(ChurnEntry, object):

    def __init__(self, item, churn):
        self.item = self.uri = resource(item)        
        self.store = churn.store
        self.make_statement = churn.make_statement
        self.retract_statement = churn.retract_statement

    def __get_comments(self):
        comments = []
        def _count(s, p, o):
            nick = self._get_comment_nick(o)
            comments.append((nick, o))
        self.store.visit(_count, (self.uri, COMMENT, None))
        def chron(a, b):
            t1 = str(self._get_comment_time(a[1]))
            t2 = str(self._get_comment_time(b[1]))
            return cmp(t1, t2)
        comments.sort(chron)
        return comments

    comments = property(__get_comments)

    def __get_time(self):
        return self.store.get_first_value(self.uri, CHUMP_TIME, '')

    time = property(__get_time)

    def __get_title(self):
        return self.store.get_first_value(self.uri, LABEL, '')

    title = property(__get_title)

    def __get_keywords(self):
        return self.store.get_first_value(self.uri, CHUMP_KEYWORDS, '')

    keywords = property(__get_keywords)

    def _get_comment_nick(self, comment):
        s_uri = self.store.get_statement_uri(self.uri, COMMENT, literal(comment))
        if s_uri:
            nick = self.store.get_first_value(s_uri, CHUMP_WHO, '')
        else:
            nick = ''
        return nick

    def _get_comment_time(self, comment):
        s_uri = self.store.get_statement_uri(self.uri, COMMENT, literal(comment))
        if s_uri:
            time = self.store.get_first_value(s_uri, CHUMP_TIME, '')
        else:
            time = ''
        return time
    
    def set_nick(self, nick):
        self.make_statement(self.uri, CHUMP_WHO, literal(nick))

    def set_time(self, time):
        self.make_statement(self.uri, CHUMP_TIME, literal(date_time(time)))

    def set_title(self, title):
        self.retract_statement(self.uri, LABEL, None)
        self.make_statement(self.uri, LABEL, literal(title))

    def set_keywords(self, keywords):
        self.retract_statement(self.uri, CHUMP_KEYWORDS, None)
        self.make_statement(self.uri, CHUMP_KEYWORDS, literal(keywords))

    def add_comment(self, comment, nick):
        comment = self._serialize_comment(nick, comment)
        self.make_statement(self.uri, COMMENT, literal(comment))
        s_uri = self.store.generate_uri()
        self.make_statement(s_uri, TYPE, STATEMENT)
        self.make_statement(s_uri, SUBJECT, self.uri)
        self.make_statement(s_uri, PREDICATE, COMMENT)
        self.make_statement(s_uri, OBJECT, literal(comment))
        self.make_statement(s_uri, CHUMP_WHO, literal(nick))
        self.make_statement(s_uri, CHUMP_TIME, literal(date_time(time.time())))

    def replace_comment_n(self, commentno, comment, nick):
        comment = self._serialize_comment(nick, comment, EntityEncoder())        
        comments = self.comments
        if commentno < len(comments) and commentno >= 0:
            s_uri = self.store.get_statement_uri(self.uri, COMMENT,
                                                 literal(comments[commentno][1]))
            if not s_uri:
                s_uri = self.store.generate_uri()
                
            self.delete_comment_n(commentno, nick)

            self.make_statement(self.uri, COMMENT, literal(comment))

            self.make_statement(s_uri, TYPE, STATEMENT)
            self.make_statement(s_uri, SUBJECT, self.uri)
            self.make_statement(s_uri, PREDICATE, COMMENT)
            self.make_statement(s_uri, OBJECT, literal(comment))
            self.make_statement(s_uri, CHUMP_WHO, literal(nick))
            t = self.store.get_first_value(s_uri, CHUMP_TIME, None)
            if not t:
                t = literal(date_time(time.time()))                    
                self.make_statement(s_uri, CHUMP_TIME, t)                    

    def delete_comment_n(self, commentno, nick):
        comments = self.comments
        if commentno < len(comments) and commentno >= 0:
            self.retract_statement(self.uri, COMMENT, literal(comments[commentno][1]))

    # TODO: This is code copied from chumpbot.py... as we do not want
    # the enclosing <comment> tag
    def _serialize_comment(self, nick, comment, encoder=EntityEncoder()):
        import re
        comment_html = encoder.encode_chars(comment)

        italic_search = re.compile('\*([^*]+)\*')
        while italic_search.search(comment_html) != None:
            match = italic_search.search(comment_html)
            comment_html = comment_html[0:match.start(1) - 1] + '<i>' + comment_html[match.start(1):match.end(1)] + '</i>' + comment_html[match.end(1) + 1:]

        img_search = re.compile('\+\[(http[^|\]]+)\]')
        while img_search.search(comment_html) != None:
            match = img_search.search(comment_html)
            comment_html = comment_html[0:match.start(1) - 2] + '<img src="' + match.group(1) + '" />' + comment_html[match.end(1) + 1:]

        titled_img_search = re.compile('\+\[([^|]+)\|([^\]]+)\]')
        while titled_img_search.search(comment_html) != None:
            match = titled_img_search.search(comment_html)
            if string.find(match.group(1),"http") == 0: # begins with http
                url_index = 1
                title_index = 2
            else:
                url_index = 2
                title_index = 1

            comment_html = comment_html[0:match.start(1) - 2] + '<img src="' + match.group(url_index) + '" alt="' + match.group(title_index) + '" />' + comment_html[match.end(2) + 1:]

        url_search = re.compile('\[(http[^|\]]+)\]')
        while url_search.search(comment_html) != None:
            match = url_search.search(comment_html)
            comment_html = comment_html[0:match.start(1) - 1] + '<a href="' + match.group(1) + '">' + match.group(1) + '</a>' + comment_html[match.end(1) + 1:]

        titled_url_search = re.compile('\[([^|]+)\|([^\]]+)\]')
        while titled_url_search.search(comment_html) != None:
            match = titled_url_search.search(comment_html)
            if string.find(match.group(1),"http") == 0: # begins with http
                url_index = 1
                title_index = 2
            else:
                url_index = 2
                title_index = 1

            comment_html = comment_html[0:match.start(1) - 1] + '<a href="' + match.group(url_index) + '">' + match.group(title_index) + '</a>' + comment_html[match.end(2) + 1:]

        return comment_html

class RedArchiver:
    def __init__(self, store, make_statement, retract_statement):
        self.store = store
        self.make_statement = make_statement
        self.retract_statement = retract_statement

    def archive_if_necessary(self, churn):
        return churn

    def retrieve_churn(self):
        churn = RedChurn(self.store, self.make_statement, self.retract_statement)
        return churn


from ircbot import SingleServerIRCBot
class RedChumpBot(DailyChumpBot):
    def __init__(self, redstore, channel, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.nickname = nickname
        self.channel = channel
        self.foocount = 0

        store = redstore.neighbourhood
        make_statement = redstore.make_statement("http://redfoot.net/")
        retract_statement = redstore.retract_statement("http://redfoot.net/")

        archiver = RedArchiver(store, make_statement, retract_statement)
        self.chump = RedChump(archiver)
