from redfoot.server.module import Module
import os

class Static(Module):

    def static(self):
        # Content-type, size, etc
        self.serve_file(self.app.request.get_path_info()[1:])

    def __getattr__(self, name):
        path_info = self.app.request.get_path_info()        
        if name == path_info:
            file = path_info[1:]
            if os.path.exists(file) and os.path.isfile(file):
                return self.static
        raise AttributeError, name
            
    def serve_file(self, file, type='text/html'):
        self.app.response.set_header("Content-Type", type)
        import shutil
        source = open(file, 'rb')
        destination = self.app.response
        shutil.copyfileobj(source, destination)
        source.close()

