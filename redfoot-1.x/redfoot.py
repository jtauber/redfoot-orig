from redcmd import RedCmd
from redfootlib.rdf.store.triple import TripleStore

class RedCmdStore(RedCmd, TripleStore): pass

if __name__ == "__main__":
    red_cmd = RedCmdStore()
    red_cmd.cmdloop()
