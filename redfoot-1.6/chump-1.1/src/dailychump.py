# Copyright (c) 2001 by Matt Biddulph and Edd Dumbill, Useful Information Company
# All rights reserved.
# 
# License is granted to use or modify this software ("Daily Chump") for
# commercial or non-commercial use provided the copyright of the author is
# preserved in any distributed or derivative work.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESSED OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# daily chump v 1.1

# $Id$ 

import string
import re
import time
import tempfile
import shutil
import os
import os.path
from EntityEncoder import EntityEncoder
from xmllib import XMLParser, procclose, illegal, tagfind

class TimeFormatter:
    def format_time(self,formattime):
        return time.strftime("%Y-%m-%d %H:%M",time.gmtime(formattime))

class StyleSheetAwareXMLParser(XMLParser):
    """ This class is needed to override a bug in Py 1.5.2's xmllib
    which meant it would reject an xml-stylesheet PI """
    def parse_proc(self, i):
        rawdata = self.rawdata
        end = procclose.search(rawdata, i)
        if end is None:
            return -1
        j = end.start(0)
        if illegal.search(rawdata, i+2, j):
            self.syntax_error('illegal character in processing instruction')
        res = tagfind.match(rawdata, i+2)
        if res is None:
            raise RuntimeError, 'unexpected call to parse_proc'
        k = res.end(0)
        name = res.group(0)
        if name == 'xml:namespace':
            self.syntax_error('old-fashioned namespace declaration')
            self.__use_namespaces = -1
            # namespace declaration
            # this must come after the <?xml?> declaration (if any)
            # and before the <!DOCTYPE> (if any).
            if self.__seen_doctype or self.__seen_starttag:
                self.syntax_error('xml:namespace declaration too late in document')
            attrdict, namespace, k = self.parse_attributes(name, k, j)
            if namespace:
                self.syntax_error('namespace declaration inside namespace declaration')
            for attrname in attrdict.keys():
                if not self.__xml_namespace_attributes.has_key(attrname):
                    self.syntax_error("unknown attribute `%s' in xml:namespace tag" % attrname)
            if not attrdict.has_key('ns') or not attrdict.has_key('prefix'):
                self.syntax_error('xml:namespace without required attributes')
            prefix = attrdict.get('prefix')
            if ncname.match(prefix) is None:
                self.syntax_error('xml:namespace illegal prefix value')
                return end.end(0)
            if self.__namespaces.has_key(prefix):
                self.syntax_error('xml:namespace prefix not unique')
            self.__namespaces[prefix] = attrdict['ns']
        else:
            if string.find(string.lower(name), 'xml ') >= 0:
                self.syntax_error('illegal processing instruction target name')
            self.handle_proc(name, rawdata[k:j])
        return end.end(0)

class Churn:
    def __init__(self,directory):
        self.database = {}
        self.directory = directory
        self.labelcount = 0
        self.set_update_time(time.time())
        self.topic=""
        self.stylesheet=""
        self.sheettype="text/css"
        self.archive_filename=""
        self._day = 0
        self._relative_uri=""

    def set_update_time(self,time):
        self.updatetime = time

    def get_update_time(self):
        return self.updatetime

    def set_relative_uri(self,uri):
        self._relative_uri=uri

    def get_relative_uri(self):
        return self._relative_uri

    def get_topic(self):
        return self.topic

    def set_topic(self,topic,savenow=1):
        self.topic = topic
        if savenow:
            self.save()
        self.update_timestamp()

    def get_stylesheet(self):
        return self.stylesheet

    def get_stylesheettype(self):
        return self.sheettype

    def set_stylesheet(self,sheet):
        self.stylesheet=sheet
        if sheet[-3:] == "xsl":
            self.sheettype="text/xsl"
        else:
            self.sheettype="text/css"

    def view_item(self, label):
        entry = self.get_entry(label)
        if entry != None:
            if entry.title == '':
                return label + ": " + entry.item
            else:
                return label + ": " + entry.title + " (" + entry.item + ")"
        else:
            return 'Label '+label+' not found.'

    def view_recent_items(self, count=5):
        labels = self._timesorted_labels()
        labels = labels[0:count]
        labels.reverse()
        message = ''
        for l in labels:
            message = message + self.view_item(l) + "\n"
        return message

    def add_item(self, item, nick, savenow=1):
        entry = ChurnEntry(item,nick)
        label = self.get_next_label()
        self.set_entry(label, entry)
        if savenow:
            self.save()
        self.update_timestamp()
        return label

    def _filename(self):
        return self.directory + "/index.xml"

    def _timesorted_labels(self):
        labels = self.database.keys()
        times = []
        for l in labels:
            times.append(self.get_entry(l).time)

        # sort list of labels by the respective time entry 
        # from the times list
        pairs = map(None,times,labels)
        pairs.sort()
        result = pairs[:]
        for i in xrange(len(result)):
            result[i] = result[i][1]
        result.reverse()
        return result

    def set_time_item(self,label,time,savenow=1):
        entry = self.get_entry(label)
        if entry != None:
            entry.set_time(time)
            if savenow:
                self.save()
            self.update_timestamp()

    def set_entry(self,label,entry):
        self.database[label] = entry

    def get_entry_count(self):
        return len(self.database.keys())

    def get_entry(self,label):
        if self.database.has_key(label):
            return self.database[label]
        else:
            return None

    def title_item(self,label,title,savenow=1):
        entry = self.get_entry(label)
        if entry != None:
            entry.set_title(title)
            if savenow:
                self.save()
            return "titled item "+label
        else:
            return 'Label '+label+' not found.'
    
    def keywords_item(self,label,dest,savenow=1):
        entry = self.get_entry(label)
        if entry != None:
            entry.set_keywords(dest)
            if savenow:
                self.save()
            return "set keywords for "+label
        else:
            return 'Label '+label+' not found.'

    def get_comments(self,label):
        entry = self.get_entry(label)
        if entry != None:
            r=entry.item + "\n"
            if entry.title != '':
                r=r+entry.title+"\n"
            if entry.keywords != '':
                r=r+"-> "+entry.keywords+"\n"
            r=r+entry.get_comments()
            return r
        else:
            return 'Label '+label+' not found.'

    def get_comment_n(self,label,commentno):
        entry = self.get_entry(label)
        if entry != None:
            comment = entry.get_comment_n(commentno-1)
            if comment != None:
                return comment
            else:
                return 'Comment '+label+str(commentno)+' not found'
        else:
            return 'Label '+label+' not found.'

    def comment_item(self,label,comment,nick,savenow=1):
        entry = self.get_entry(label)
        if entry != None:
            entry.add_comment(comment,nick)
            if savenow:
                self.save()
            return "added comment "+label+str(entry.num_comments())
        else:
            return 'Label '+label+' not found.'

    def replace_comment_n(self,label,comment,commentno,nick):
        entry = self.get_entry(label)
        if entry != None:
            oldcomment = entry.get_comment_n(commentno-1)
            if oldcomment != None:
                entry.replace_comment_n(commentno-1,comment,nick)
                self.save()
                return "replaced comment "+label+str(commentno)
            else:
                return 'Comment '+label+str(commentno)+' not found'
        else:
            return 'Label '+label+' not found.'

    def delete_comment_n(self,label,commentno,nick):
        entry = self.get_entry(label)
        if entry != None:
            comment = entry.get_comment_n(commentno-1)
            if comment != None:
                entry.delete_comment_n(commentno-1,nick)
                self.save()
                return "deleted comment "+label+str(commentno)
            else:
                return 'Comment '+label+str(commentno)+' not found'
        else:
            return 'Label '+label+' not found.'

    def save(self):
        name = tempfile.mktemp()
        out_file = open(name,"w")
        out_file.write(self.serialize())
        out_file.write("\n")
        out_file.close()
        if os.path.isfile(self._filename()):
            os.remove(self._filename())
        shutil.copy(name,self._filename())
        shutil.copy(name,self.get_archive_filename())
        os.unlink(name)

    def set_archive_filename(self,fname):
        self.archive_filename=fname

    def get_archive_filename(self):
        return self.archive_filename

    def deserialize(self,data):
        c = ChurnParser()
        c.set_churn(self)
        c.feed(data)
        c.close()

    def serialize(self):
        encoder = EntityEncoder()
        serialized='<!DOCTYPE churn>\n'
        if self.get_stylesheet()!="":
            serialized = serialized + '<?xml-stylesheet href="'+\
                         encoder.encode_chars(self.get_stylesheet())+\
                         '" type="'+\
                         self.get_stylesheettype()+'"?>'+"\n"
        serialized = serialized + "<churn>\n"

        serialized = serialized + '<last-updated value="'
        serialized = serialized + "%f" % self.updatetime
        serialized = serialized + '">'
        serialized = serialized + encoder.encode_chars(TimeFormatter().format_time(self.updatetime))+"</last-updated>\n"

        serialized = serialized + '<relative-uri-stub value="' + encoder.encode_chars(self.get_relative_uri()) + '"/>'+"\n"
        serialized = serialized + '<itemcount value="'
        serialized = serialized + "%d" % self.get_entry_count()
        serialized = serialized + '" />\n'

        serialized = serialized + "<topic>"+encoder.encode_chars(self.topic)+"</topic>\n"

        for x in self._timesorted_labels():
            entry = self.get_entry(x)
            serialized = serialized + entry.serialize()
        serialized = serialized + "</churn>"
        return serialized

    def get_next_label(self):
        label = self.number_to_label(self.labelcount)
        self.labelcount = self.labelcount + 1
        return label

    def number_to_label(self,number):
        if number < 26:
            return chr(number + 65)

        if number == 26:
            return 'AA'

        count = number - 26
        label = ''
        while count > 0:
            label = chr((count % 26) + 65) + label
            count = count / 26

        if number < 52:
            return 'A' + label
        else:
            return label

    def update_timestamp(self):
        self.set_update_time(time.time())

class ChurnEntry:
    def __init__(self,item,nick):
        self.item = item
        self.nick = nick
        self.comments = []
        self.set_time(time.time())
        self.title = ''
        self.keywords = ''

    def serialize(self):
        encoder = EntityEncoder()
        serialized = ''
        serialized = serialized + "<link"
        if self.item == 'blurb':
           serialized = serialized + ' type="blurb"'
        serialized = serialized + ">\n"
        serialized = serialized + '<time value="'
        serialized = serialized + "%f" % self.time
        serialized = serialized + '">'
        serialized = serialized + encoder.encode_chars(TimeFormatter().format_time(self.time))
        serialized = serialized + "</time>\n"
        serialized = serialized + "<keywords>" + encoder.encode_chars(self.keywords) + "</keywords>\n"
        if not self.item == 'blurb':
           serialized = serialized + "<url>"+encoder.encode_chars(self.item)+"</url>\n"
        serialized = serialized + "<nick>"+encoder.encode_chars(self.nick)+"</nick>\n"
        if self.title != '':
            serialized = serialized + "<title>"+encoder.encode_chars(self.title)+"</title>\n"
        for c in self.comments:
            nick = c[0]
            comment = c[1]
            serialized = serialized + self.serialize_comment(nick,comment,encoder)
        serialized = serialized + "</link>\n"
        return serialized

    def serialize_comment(self,nick,comment,encoder):
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

        serialized = ''
        serialized = serialized + '<comment nick="' + nick+ '">'
        serialized = serialized + comment_html
        serialized = serialized + "</comment>\n"
        return serialized

    def set_time(self,time):
        self.time = time

    def add_comment(self,comment,nick):
        self.comments.append([nick,comment])

    def set_title(self,title):
        self.title = title

    def set_keywords(self,keywords):
        self.keywords = keywords

    def get_comments(self):
        comments = ''
        cno=1
        for c in self.comments:
            nick = c[0]
            comment = c[1]
            comments = comments + '(' +str(cno)+':' + nick+ ') '
            comments = comments + comment
            comments = comments + "\n"
            cno=cno+1
        return comments

    def get_comment_n(self,commentno):
        if commentno < len(self.comments) and commentno >= 0:
            return "(" + self.comments[commentno][0] + ") " + self.comments[commentno][1]
        else:
            return None

    def replace_comment_n(self,commentno,comment,nick):
        if commentno < len(self.comments) and commentno >= 0:
            self.comments[commentno]=[nick,comment]

    def num_comments(self):
        return len(self.comments)

    def delete_comment_n(self,commentno,nick):
        if commentno < len(self.comments) and commentno >= 0:
            self.comments.remove(self.comments[commentno])

class ChurnParser(StyleSheetAwareXMLParser):
    def __init__(self):
        XMLParser.__init__(self)
        self._data = ''
        self._in_a = 0
        self._a_title = ''
        self._a_href = ''
        self._entries = []
        self._current_entry = {}

    def set_churn(self,churn):
        self.churn = churn

    def get_churn(self):
        return self.churn

    def start_link(self,attrs):
        self._current_entry['title'] = ''
        self._current_entry['time'] = 0
        self._current_entry['nick'] = ''
        self._current_entry['item'] = ''
        self._current_entry['keywords'] = ''
        self._current_entry['comments'] = []
        if attrs.has_key('type'):
            type = attrs['type']
            if type == 'blurb':
                self._current_entry['blurb'] = 1
        else:
            self._current_entry['blurb'] = 0

    def start_a(self,attrs):
        if self._in_comment == 1:
            if(attrs.has_key('href')):
                self._a_href = attrs['href']
            else:
                self._a_href = ''
            self._a_title = ''
            self._in_a = 1

    def start_img(self,attrs):
        if self._in_comment == 1:

            if(attrs.has_key('src')):
                self._img_src = attrs['src']
            else:
                self._img_src = ''

            if(attrs.has_key('alt')):
                self._img_title = attrs['alt']
            else:
                self._img_title = ''

    def start_i(self,attrs):
        self._data = self._data + '*'

    def end_i(self):
        self._data = self._data + '*'

    def end_img(self):
        if self._img_title != '' and self._img_src != '' and self._img_src != self._img_title:
            self._data = self._data + '+[' + self._img_title + '|' + self._img_src + ']'
        elif self._img_src != '':
            self._data = self._data + '+[' + self._img_src + ']'

    def end_a(self):
        if self._a_title != '' and self._a_href != '' and self._a_href != self._a_title:
            self._data = self._data + '[' + self._a_title + '|' + self._a_href + ']'
        elif self._a_href != '':
            self._data = self._data + '[' + self._a_href + ']'
        self._in_a = 0

    def start_itemcount(self,attrs):
        if attrs.has_key('value'):
            self._itemcount = string.atoi(attrs['value'])

    def unknown_starttag(self,tag,attrs):
        self._tag_name = tag
        self._data = ''
        if tag == 'last-updated':
            if attrs.has_key('value'):
                self._last_updated = string.atof(attrs['value'])
            else:
                self._last_updated = time.time()
        if tag == 'comment':
            self._current_entry['comment_nick'] = attrs['nick']
            self._in_comment = 1
        if tag == 'time':
            if attrs.has_key('value'):
                self._current_entry['time'] = string.atof(attrs['value'])
            else:
                self._current_entry['time'] = time.time()

    def end_title(self):
        self._current_entry['title'] = self._data

    def end_keywords(self):
        self._current_entry['keywords'] = self._data

    def end_url(self):
        self._current_entry['item'] = self._data

    def end_nick(self):
        self._current_entry['nick'] = self._data

    def end_comment(self):
        self._in_comment = 0
        self._current_entry['comments'].append([self._data,self._current_entry['comment_nick']])

    def end_link(self):
        self._entries.append(self._current_entry)
        self._current_entry = {}

    def end_churn(self):
        self._entries.reverse()

        for a in self._entries:
            if a['blurb'] == 1:
                a['item'] = "blurb"
            label = self.churn.add_item(a['item'],a['nick'],0)
            if a['title'] != '':
                self.churn.title_item(label,a['title'],0)
            if a['keywords'] != '':
                self.churn.keywords_item(label,a['keywords'],0)
            for c in a['comments']:
                self.churn.comment_item(label,c[0],c[1],0)
            self.churn.set_time_item(label,a['time'],0)

        self.churn.set_update_time(self._last_updated)

    def handle_data(self,text):
        if self._in_a == 1:
            self._a_title = self._a_title + text
        else:
            self._data = self._data + text


class LastUpdatedParser(StyleSheetAwareXMLParser):
    def unknown_starttag(self,tag,attrs):
        if tag == 'last-updated':
            self.lu = attrs['value']

    def get_last_updated(self):
        return string.atof(self.lu)

class DailyChump:
    def __init__(self, directory):
        self.archiver = FileArchiver(directory)
        self.churn = self.archiver.retrieve_churn()

    def set_topic(self,topic):
        self.churn = self.archiver.archive_if_necessary(self.churn)
        self.churn.set_topic(topic)

    def view_recent_items(self,count=5):
        return self.churn.view_recent_items(count)

    def get_database(self):
        return self.churn.serialize()

    def set_stylesheet(self, sheet):
        self.churn.set_stylesheet(sheet)

    def process_input(self,nick,msg):
        blurbmatch = re.compile("BLURB:\s*(.*)")
        urlmatch = re.compile("(https?:\/\/[^ ]+)")
        titlematch = re.compile("([A-Z]+):\|\s*(.*)")
        commentmatch = re.compile("([A-Z]+):\s*(.*)")
        destmatch = re.compile("([A-Z]+):\->\s*(.*)")
        comrepmatch = re.compile("([A-Z]+)(\d+):\s*(.*)")

        um = urlmatch.match(msg)
        bm = blurbmatch.match(msg)
        tm = titlematch.match(msg)
        cm = commentmatch.match(msg)
        dm = destmatch.match(msg)
        rm = comrepmatch.match(msg)

        if um:
            self.churn = self.archiver.archive_if_necessary(self.churn)
            url = um.group(1)
            label = self.churn.add_item(url,nick)
            return label+": "+url+" from "+nick

        elif bm:
            self.churn = self.archiver.archive_if_necessary(self.churn)
            item = "blurb"
            title = bm.group(1)
            label = self.churn.add_item(item,nick)
            msg = self.churn.title_item(label,title)
            return label+": "+title+" from "+nick

        elif tm:
            label = tm.group(1)
            title = tm.group(2)
            return self.churn.title_item(label,title)

        elif dm:
            label = dm.group(1)
            dest = dm.group(2)
            return self.churn.keywords_item(label, dest)

        elif cm:
            label = cm.group(1)
            comment = cm.group(2)
            if comment == '':
                return self.churn.get_comments(label)
            else: 
                return self.churn.comment_item(label,comment,nick)
        elif rm:
            label = rm.group(1)
            commentno = int(rm.group(2))
            comment = rm.group(3)
            if comment == '':
                return self.churn.get_comment_n(label,commentno)
            elif comment == '""':
                return self.churn.delete_comment_n(label,commentno,nick)
            else:
                return self.churn.replace_comment_n(label,comment,commentno,nick)

        else:
            return

class FileArchiver:
    def __init__(self, directory):
        self.filename = directory + os.sep + "index.xml"
        self.directory = directory

    def archive_if_necessary(self,churn):
        date = churn.updatetime
        if self.should_archive(date):
            # create a new churn
            churn = Churn(self.directory)
            churn.set_archive_filename(self.prepare_filename(time.time()))
            churn.set_relative_uri(self.prepare_relative_uri(time.time()))
        return churn

    def retrieve_churn(self):
        churn = Churn(self.directory)

        if os.path.isfile(self.filename):
            date = self.get_date(self.filename)
            if self.should_archive(date):
                #print "Archiving current file"
                destination = self.prepare_filename(date)
                os.rename(self.filename,destination)
            else:
                #print "Reading current file"
                file = open(self.filename,'r')
                data = file.read()
                file.close()
                churn.deserialize(data)

        churn.set_archive_filename(self.prepare_filename(time.time()))
        churn.set_relative_uri(self.prepare_relative_uri(time.time()))
        churn.save()
        return churn

    def should_archive(self,date):
        date_components = time.gmtime(date)
        file_year = date_components[0]
        file_month = date_components[1]
        file_day = date_components[2]

        date_components = time.gmtime(time.time())
        year = date_components[0]
        month = date_components[1]
        day = date_components[2]

        if(year == file_year and month == file_month and day == file_day):
            return 0
        else:
            return 1

    def prepare_filename(self,date):
        date_components = time.gmtime(date)
        year = "%d" % date_components[0]
        month = "%02d" % date_components[1]
        day = "%02d" % date_components[2]
        dir = self.directory + os.sep + string.join([year, month, day],os.sep)
        if not os.path.isdir(dir):
            os.makedirs(dir)

        filename = string.join([year, month, day],"-")
        filename = dir + os.sep + filename
        filename = filename + ".xml"
        return filename

    def prepare_relative_uri(self,date):
        date_components = time.gmtime(date)
        year = "%d" % date_components[0]
        month = "%02d" % date_components[1]
        day = "%02d" % date_components[2]
        dir = string.join([year, month, day],os.sep)
        filename = string.join([year, month, day],"-")
        filename = dir + os.sep + filename
        return filename

    def get_date(self,filename):
        file = open(filename,'r')
        contents = file.read()
        file.close()

        parser = LastUpdatedParser()
        parser.feed(contents)

        return parser.get_last_updated()
