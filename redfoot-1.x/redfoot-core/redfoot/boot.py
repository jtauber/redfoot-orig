import redfoot

from redfoot.module import App, ParentModule, Module
from redfoot.server import RedServer
from redfoot.rdf.objects import resource, literal

from redfoot.util import encode_URI

APP = resource("http://redfoot.net/2002/04/08/APP")

from traceback import print_exception            
from StringIO import StringIO
import sys

class Boot(App):
    def __init__(self, rednode):
        App.__init__(self, rednode)
        self.server = None
        self.current = None
        
    def handle_request(self, request, response):
        try:
            self.last = 0
            super(ParentModule, self).handle_request(request, response)
            response.set_header("Expires", "-1")
            
            path = request.get_path_info()
            if path=="/":
                self.root_facet(request, response)
            elif path=="/app":
                self.app_facet(request, response)
            else:
                pass
        except:
            etype, value, tb = sys.exc_info()
            sio = StringIO()
            print_exception(etype, value, tb, None, sio)
            response.write("""\
<h1>Exception Occured</h1>
<p>The following exception occured in the Bootstrap App</p>
<pre>%s</pre>
<p><a href="">Refresh</a></p>
""" % sio.getvalue())
        response.close()

    def root_facet(self, request, response):        
        app = self.rednode.get_first_value(resource(self.rednode.uri), APP, '')        
        response.write("""
<html><h1>Default Redfoot Bootstrap Application</h1>
  <p>
    This application is used to start and stop servers for the
    applications known to this Rednode.
  </p>
  <h2>Known Applications</h2>
  <ul>""")
        for module in redfoot.modules.keys():
            if issubclass(redfoot.modules[module], App):
                if module==app:
                    selected = ' selected="true"'
                else:
                    selected = ''
                response.write("""    <li><a href="app?uri=%s">%s</a></li>
  """ % (encode_URI(module), module))
            
        response.write("""
  </ul>            
 <form id="config_form" action="" method="post">
  <h2>App URI:</h2>
  <select type="text" name="app_uri" onChange="config_form.processor.value='update'; config_form.submit()">""")

        for module in redfoot.modules.keys():
            if issubclass(redfoot.modules[module], App):
                if module==app:
                    selected = ' selected="true"'
                else:
                    selected = ''
                response.write("""<option value="%s"%s>%s</option>""" % (module, selected, module))
        response.write("""            
  </select>
  <input type="hidden" name="processor" value="update"></input>
 </form>
 """)
        response.write("""
            <h2><a href="http://localhost/">foo running on http://localhost/</a></h2>
</html>
""")

    def app_facet(self, request, response):
        uri = request.get_parameter('uri', '')
        response.write("""
<html>
  <h1>App</h1>
  <h2>%s</h2>
  <h3>Instances:</h3>
  <ul>
    <li>Running at <a href="">'':80/no_path_for_now</a> <a href="">remove</a></li>
    <li>Running at <a href="">'':8080</a> <a href="">remove</a></li>
  </ul>
  <div>Add instance: Address: <input type="text"></input>, Port: <input type="text"></input> <input name="start" value="start" type="submit"></input></div>

          <p>Also, for now, only allow one app per server -- so, if there already is a server for (address, port) then replace its handler.</p>
        </html>
""" % (uri,))        
        
    def do_update(self, request, response):
        app_uri = request.get_parameter('app_uri', None)
        rednode = self.rednode
        if app_uri:
            rednode.remove(resource(rednode.uri), APP, None)
            rednode.add(resource(rednode.uri), APP, resource(app_uri))

            app_class = self.get_app_class()
            if app_class:
                if not self.server:
                    self.server = RedServer('', 80)
                if self.current:
                    self.server.remove_handler(self.current)
                self.current = app_class(rednode)
                self.server.add_handler(self.current)
                self.last = 1

    def get_app_class(self):
        app_class = None
        rednode = self.rednode
        app = rednode.get_first_value(resource(rednode.uri), APP, None)
        if app:
            app_class = redfoot.modules.get(app, None)
            if not app_class:
                print "Warning: Module '%s' not found" % app
                print "... known modules include", redfoot.modules.keys()
        return app_class
        
