from redfoot import version

def run():
    if hasattr(version, "VERSION"):
        return (1, "TEST PASSED")
    else:
        return (0, "TEST FAILED")







