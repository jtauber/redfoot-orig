if __name__ == "__main__":
    from redfoot.server import RedServer
    from redfoot.rednode import RedNode

    #from socket import gethostname
    #hostname = gethostname()
    hostname = 'localhost'
    port = 8000
    server = RedServer((hostname, port))

    if port==80:
        uri = "http://%s/" % hostname
    else:
        uri = "http://%s:%s/" % (hostname, port)

    node = RedNode()
    node.local.load("sample2.rdf", uri )

    server.run_redpage("sample2.xml", node)






