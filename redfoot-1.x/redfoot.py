import sys

def usage():
    print """\
USAGE: redfoot.py <redfoot command file>

    options:
           [-h,--help]

"""    
    sys.exit(-1)




if __name__ == "__main__":
    import dev_hack

    import sys, getopt
    from redcmd import RedCmd

    try:
        optlist, args = getopt.getopt(sys.argv[1:],
                                      'h:',
                                      ["help"])
    except getopt.GetoptError, msg:
        print msg
        usage()
    
    red_cmd = RedCmd()    

    argv = sys.argv
    for arg in sys.argv[1:]:
        file = open(arg, "r")
        for line in file:
            line = line.strip()
            # Commands where repeating due to file appear double spaced
            if line:
                red_cmd.cmdqueue.append(line)
    red_cmd.cmdloop()
