####
from redfootlib.server.module import App
from redfootlib.rdf.objects import resource, literal
from redfootlib.rdf.const import TYPE, LABEL, COMMENT
from redfootlib.rdf.query.functors import sort
from sniffer import SNIFFED, SNIFFABLE, SNIFFED_ON, SNIFFED_FROM

from functors import slice  

class LinkApp(App):

    def handle_request(self, request, response):
        start = int(request.get_parameter("start", "0"))
        end = int(request.get_parameter("end", "30"))
        rednode = self.rednode
        
        def display_link(s, p, o):
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
        # TODO: split into two comparators... reverse and chron
        def reverse_chron((s1, p1, o1), (s2, p2, o2)):
            date_a = rednode.get_first_value(s1, SNIFFED_ON, '')
            date_b = rednode.get_first_value(s2, SNIFFED_ON, '')
            return 0-cmp(str(date_a), str(date_b))

        callback = lambda s, p, o: display_link(s, p, o)
        sort(reverse_chron, rednode.visit)(slice(callback, start, end), (None, TYPE, SNIFFED))

        response.write("""\
  </ul>        
</html>
""");
        response.close()
    


