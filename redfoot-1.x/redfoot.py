import dev_hack

import sys

from redcmd import RedCmd

if __name__ == "__main__":
    red_cmd = RedCmd()    

    argv = sys.argv
    if len(argv)==2:
        file = open(argv[1], "r")
        for line in file:
            red_cmd.cmdqueue.append(line)

    red_cmd.cmdloop()
