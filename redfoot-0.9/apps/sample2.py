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
    node.connectTo("rssSchema.rdf", None)
    node.connectTo("dces.xml", None)    
    #node.connectTo("http://xmlhack.com/rss10.php", "http://xmlhack.com/rss10.php")
    node.connectTo("xmlhack.rdf", "xmlhack.rdf")        

    server.run_redpage("sample2.xml", node)






