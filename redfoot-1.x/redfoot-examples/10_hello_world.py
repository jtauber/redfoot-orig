#

from redfoot.module import App

class HelloWorld(App):

    def handle_request(self, request, response):
        response.write("""\
<html>
  <title>Hello World!</title>
  <h1>Hello World!</h1>
  <h2>Pure Python</h2>
</html>
""");
        response.close()

# 
from redfoot.server import register_app
register_app("http://redfoot.net/2002/04/08/HelloWorld", HelloWorld)
