#################################################
# RUN -- PYTHON SCRIPT USED TO RUN REDFOOT APPS #
#################################################

import dev_hack # Needed only when developing redfoot-core


#### IMPORTS

from redfoot.rednode import RedNode
from redfoot.server import RedServer
from redfoot import get_apps as get_app_classes
from redfoot.command_line import process_args


# Let redfoot.command_line process_args for us
(uri, location, address, port) =  process_args()

# Create a RedNode
rednode = RedNode()

# Load RDF data from location using uri as the base URI, creating a
# file if one does not already exist.
rednode.load(location, uri, 1)


app_classes = get_app_classes()
if len(app_classes)>0:
    # use the first one as the one to run    
    (app_class_uri, AppClass) = app_classes[0] 
else:
    raise "No Apps Found"

# Create a RedServer listening on address, port
server = RedServer(address, port)

# Create an instance of AppClass to add to our RedServer
app = AppClass(rednode)
server.add_app(app)

# Run the App
server.run() # blocks until server is shutdown


