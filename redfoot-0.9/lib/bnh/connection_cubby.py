# $Header$
#
#  Copyright (c) 2000, James Tauber and Daniel Krech
#
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the
#     distribution.
#
#   * Neither name of James Tauber nor Daniel Krech may be used to
#     endorse or promote products derived from this software without
#     specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
#  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
#  OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
#  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
#  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
#  DAMAGE.
#


from threading import RLock
from threading import Condition

class ConnectionCubby:

    def __init__(self, limit):
        self.mon = RLock()
        self.rc = Condition(self.mon)
        self.wc = Condition(self.mon)
        self.limit = limit
        self.queue = []

    def put(self, item):
        self.mon.acquire()
        while len(self.queue) >= self.limit:
            self.wc.wait()
        self.queue.append(item)
        self.rc.notify()
        self.mon.release()

    def get(self):
        self.mon.acquire()
        if not self.queue:
            item = None
        else:
            item = self.queue[0]
            del self.queue[0]
            self.wc.notify()
        self.mon.release()
        return item

    def empty(self):
        if not self.queue:
            return 1
        else:
            return 0
        

    def wait(self, timeout=None):
        self.mon.acquire()
        self.rc.wait(timeout)
        self.mon.release()

    def notify(self):
        self.mon.acquire()
        self.rc.notify()
        self.mon.release()

#~ $Log$
#~ Revision 7.0  2001/03/26 23:41:04  eikeon
#~ NEW RELEASE
#~
#~ Revision 6.1  2001/03/26 20:19:00  eikeon
#~ removed old header
#~
