Medusa is a 'server platform' -- it provides a framework for
implementing asynchronous socket-based servers (TCP/IP and on Unix,
Unix domain sockets).

An asynchronous socket server is a server that can communicate with
many other socket clients and servers simultaneously, by multiplexing
I/O within a single process/thread.  In the context of an HTTP server,
this means a single process can serve hundreds or even thousands of
clients, depending only on the operating system's configuration and
limitations.

There are several advantages to this approach:
     
  o  performance - no fork() or thread() start-up costs per hit.

  o  scalability - the overhead per client can be kept rather small,
     on the order of several kilobytes of memory.

  o  persistence - a single-process server can easily coordinate the
     actions of several different connections.  This makes things like
     proxy servers and gateways easy to implement.  It also makes it
     possible to share resources like database handles.

Medusa includes HTTP, FTP, and 'monitor' (remote python interpreter)
servers.  Medusa can simultaneously support several instances of
either the same or different server types - for example you could
start up two HTTP servers, an FTP server, and a monitor server.  Then
you could connect to the monitor server to control and manipulate
medusa while it is running.

Other servers and clients have been written (SMTP, POP3, NNTP), and
several are in the planning stages.  

Medusa was originally written by Sam Rushing <rushing@nightmare.com>,
and its original Web page is at <http://www.nightmare.com/medusa/>. After
Sam moved on to other things, A.M. Kuchling <akuchlin@mems-exchange.org> 
took over maintenance of the Medusa package.

--amk


PS: This is version 0.5.2 of medusa[1] with one patch applied to fix a
bug in composit producer[2]. This fix has already been made to version
0.5.3 and should not be needed after its release. --eikeon

[1] http://www.amk.ca/python/code/medusa.html)

[2] diff -wr medusa/producers.py medusa-0.5.2/producers.py
3c3
< RCS_ID = '$Id$'
---
> RCS_ID = '$Id$'
154c154
<             p = self.producers[0] 
---
>             p = self.producers.pop(0)
159c159
<                 self.producers.pop(0) 
---
>                 self.producers.pop()

