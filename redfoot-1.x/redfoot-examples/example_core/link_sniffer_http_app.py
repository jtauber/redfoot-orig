####
from redfoot.server.module import App
from redfoot.rdf.objects import resource, literal
from redfoot.rdf.const import TYPE, LABEL, COMMENT
from link_sniffer import SNIFFED, SNIFFABLE, SNIFFED_ON, SNIFFED_FROM, RUN


class LinkApp(App):

    def display_link(self, request, response, s, p, o):
        rednode = self.rednode
        label = rednode.label(s)
        sniffed_on = rednode.get_first_value(s, SNIFFED_ON, '??')
        sniffed_from = rednode.get_first_value(s, SNIFFED_FROM, None)
        if sniffed_from:
            sniffed_from = rednode.label(sniffed_from)
        else:
            sniffed_from = "unknown"

        response.write("""\
    <p>
      <div><a href="%s">%s</a></div>
      <div class="small">%s</div>
      <div class="small">
        <span class="label">from:</span>&nbsp;%s <span class="label">on:</span>&nbsp;%s
      </div>      
    </p>""" % (s, label, s, sniffed_from, sniffed_on))
    
    def handle_request(self, request, response):
        start = int(request.get_parameter("start", "0"))
        end = int(request.get_parameter("end", "30"))
        sniffer = self.rednode
        response.write("""\
<!DOCTYPE html 
     PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
     "DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <title>Link Sniffer</title>
    <style>
      body { 
        margin: 2% 4%; 
        background:  #FFF;
        color:       #000;
        font-family: "Trebuchet MS", sans-serif;
        font-size:   10pt;
      }
      a { 
        color: #000;
        text-decoration: underline; 
        font-weight: bold; 
      }
      a:hover {
        color: #333;
        text-decoration: underline; 
      }
      .small {
        font-size: 8pt;
      }
      .label {
	color: #999
      }
    </style>
  </head>
  <h1>Links</h1>
  <ul>
""")
        callback = lambda s, p, o: self.display_link(request, response, s, p, o)
        from functors import slice        
        sort(sniffer.reverse_chron, sniffer.visit)(slice(callback, start, end), (None, TYPE, SNIFFED))

        response.write("""\
  </ul>        
</html>
""");
        response.close()
    


def run_app(sniffer):
    """Runs the LinkApp on a RedServer for the given sniffer."""
    from redfoot.server import RedServer

    server = RedServer('', 9090)

    app = LinkApp(sniffer)
    server.add_app(app)

    # Run the server in a thread... otherwise we block on server.run() and
    # do not get past it until the server stops. Also, set the thread to
    # be a daemon thread so it goes away when we do.

    import threading
    t = threading.Thread(target = server.run, args = ())
    t.setDaemon(1)
    t.start()
