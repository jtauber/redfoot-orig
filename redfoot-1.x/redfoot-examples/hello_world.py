#

from redfootlib.server.module import App
from redfootlib.server import register_app


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
register_app("http://redfoot.net/2002/04/08/HelloWorld", HelloWorld)
