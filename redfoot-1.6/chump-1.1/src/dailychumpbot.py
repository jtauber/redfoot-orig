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

# $Id$

# daily chump v 1.0

## irc interface to the chump engine

from dailychump import DailyChump
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, irc_lower
import string
import time
import re

class DailyChumpBot(SingleServerIRCBot):
    def __init__(self, directory, channel, nickname,
                 server, port=6667, sheet=None):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.nickname = nickname
        self.channel = channel
        self.foocount = 0
        self.chump = DailyChump(directory)
        if sheet!=None:
            self.chump.set_stylesheet(sheet)
        self.start()

    def on_topic(self,c,e):
        if e.arguments()[0] == self.channel:
            topic = e.arguments()[1]
        else:
            topic = e.arguments()[0]
        self.chump.set_topic(topic)

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        nick = nm_to_n(e.source())
        output = self.do_command(nick, e.arguments()[0])
        if output != None:
            self.privmsg_multiline(c,nick,output)

    def on_pubmsg(self, c, e):
        msg = e.arguments()[0]
        nick = nm_to_n(e.source())

        a = string.split(msg, ":", 1)

        if len(a) > 1 and irc_lower(a[0]) == irc_lower(self.connection.get_nickname()):
            output = self.do_command(nick, string.strip(a[1]))
        else:
            output = self.chump.process_input(nick, msg)

        if output != None:
            self.notice_multiline(c,output)

    def notice_multiline(self,c,msg):
        for x in string.split(msg,"\n"):
            c.notice(self.channel, x)
            time.sleep(1)

    def privmsg_multiline(self,c,nick,msg):
        for x in string.split(msg,"\n"):
            c.privmsg(nick, x)
            time.sleep(1)

    def do_command(self, nick, cmd):
        c = self.connection

        if cmd == "database":
            data = self.chump.get_database()
            return data 
            #self.notice_multiline(c,data)
        elif cmd == "disconnect":
            self.disconnect()
        elif cmd == "help":
            #self.notice_multiline(c,
            return "Post a URL by saying it on a line on its own\n"+ "To post an item without a URL, say BLURB:This is the title\n"+ "I will reply with a label, for example A\n"+ "You can then append comments by saying A:This is a comment\n"+ "To title a link, use a pipe as the first character of the comment\n"+ "Eg. A:|This is the title\n"+ "To see the last 5 links posted, say "+self.nickname+":view\n" "For more features, say "+self.nickname+":morehelp\n"
                #)
        elif cmd == "morehelp":
            #self.notice_multiline(c,
            return "Put emphasis in a comment by using *asterisks*\n"+ "To create an inline link in a comment, say:\n"+ "A:Look at [this thing here|http://pants.heddley.com]\n"+ "You can also link to inline images in a comment:\n"+ "A:Chump logo +[alt-text|http://pants.heddley.com/chump.png]\n"+ "To see the last n links, say "+self.nickname+":view n (where n is a number)\n"+ "To see the details of a link labelled A, say A: on a line on its own\n"+ "To view a particular comment, say An:, where n is the number of the comment\n" + "To replace, say, the second comment on a link labelled A, say A2:replacement_text\n" + "To delete the second comment on a link labelled A, say A2:\"\"\n" + "To set keywords for a link labelled A, say A:->keyword1 keyword2 etc.\n" + "Send any comments or questions to chump@heddley.com\n"
                #)
        elif cmd == "foo":
            c.action(self.channel,"falls down a well.")
            self.foocount = self.foocount + 1
        elif cmd == "unfoo":
            if self.foocount > 0:
                c.action(self.channel,"clambers out of a well.")
                self.foocount = self.foocount - 1
            else:
                c.action(self.channel,"is not in a well, silly.")
        elif string.find(cmd,"view") == 0:
            viewmatch = re.compile("view\s+(\d+)")
            vm = viewmatch.match(cmd)
            if vm != None:
                count = string.atoi(vm.group(1))
                #self.notice_multiline(c,self.chump.view_recent_items(count))
                return self.chump.view_recent_items(count)
            else:
                #self.notice_multiline(c,self.chump.view_recent_items())
                return self.chump.view_recent_items()
        elif cmd == "die" or cmd == "depart" or cmd == "leave":
            self.die()
        else:
            #c.notice(nick, "Not understood: " + cmd)
            return "Not understood: " + cmd

def main():
    import sys
    import getopt
    args = sys.argv[1:]
    optlist, args = getopt.getopt(args,'s:p:c:n:d:e:h')
    port = 6667

    directory = ''
    channel = ''
    nickname = ''
    server = ''
    sheet = None

    for o in optlist:
        name = o[0]
        value = o[1]
        if name == '-s':
            server = value
        elif name == '-p':
            try:
                port = int(value)
            except ValueError:
                print "Error: Erroneous port."
                sys.exit(1)
        elif name == '-c':
            channel = value
        elif name == '-n':
            nickname = value
        elif name == '-d':
            directory = value
        elif name == '-e':
            sheet = value

    if(directory != '' and channel != '' and nickname != '' and server != ''):
        bot = DailyChumpBot(directory, channel, nickname, server, port, sheet)
        bot.start()
    else:
        print "Commandline options:"
        print
        print "  -s server"
        print "  [-p port]"
        print "  -n nick"
        print "  -c channel"
        print "  -d directory for XML store"
	print "  -e name of stylesheet"
        print

if __name__ == "__main__":
    main()
