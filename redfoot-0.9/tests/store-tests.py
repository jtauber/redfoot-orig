from redfoot.store import TripleStore


def test_1():
    "Simple test of store."
    
    ts = TripleStore()
    ts.put("s1", "p1", "v")
    ts.put("s1", "p2", "v")
    ts.put("s2", "p", "v")
    ts.put("s3", "p", "v")

    print len(ts.get())
    ts.remove("s1")
    print len(ts.get())

test_1()



