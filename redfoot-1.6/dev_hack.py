# If redfoot is not installed set the path to use the one relative to
# us. This is useful for developing or experimenting with the core
# code.
try:
    import redfootlib
except:
    # redfoot must not be installed, try adding    
    import sys, os

    # use directory of script importing us as base for relative names
    RFHOME = os.path.dirname(sys.argv[0])

    paths = ["lib", "examples", "medusa-0.5.2-rf1/", "chump-1.1/src/"]
    
    for path in paths:
        sys.path.append(os.path.join(RFHOME, path))
