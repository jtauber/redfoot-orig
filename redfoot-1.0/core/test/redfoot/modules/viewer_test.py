
from redfoot.server.http.daemon import RedDaemon

port = 8000
daemon = RedDaemon(("", port), "redfoot.modules.viewer")
daemon.run()


