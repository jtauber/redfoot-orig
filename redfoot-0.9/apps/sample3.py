if __name__ == "__main__":
    from redfoot.server import RedServer
    from redfoot.rednode import RedNode

    hostname = 'localhost'
    port = 8000
    server = RedServer((hostname, port))

    uri = "http://%s:%s/" % (hostname, port)

    node = RedNode()
    node.local.load("sample3.rdf", uri )
    server.run_redpage("sample3.xml", node)






