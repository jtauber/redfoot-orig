# If redfoot is not installed set the path to use the one relative to
# us. This is useful for developing or experimenting with the core
# code.
try:
    import redfootlib
except:
    # redfoot must not be installed, try adding
    import sys
    sys.path.extend(("./redfoot-core", "./redfoot-components", "./redfoot-examples"))
