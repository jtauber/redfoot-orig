if __name__ == "__main__":

    from redfoot.rednode import RedNode
    node = RedNode()
    node.local.load("neighbour-sample.rdf", None)
    node.connectTo("neighbour.rdf", None)

    from redfoot.server import RedServer
    server = RedServer(('', 8000))
    server.run_redpage("neighbours.xml", node)






