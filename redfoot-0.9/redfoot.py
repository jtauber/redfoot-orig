# $Header$

if __name__ == '__main__':
    import sys
    from redfoot.server import runServer
    from redfoot.editor import PeerEditor
    runServer(sys.argv[1:], PeerEditor)

# $Log$
