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

def test_2():
    "Test of MultiStore."
    
    from redfoot.store import MultiStore
    ms = MultiStore()

    ts1 = TripleStore()
    ts1.put("s1", "p1", "v")
    ts1.put("s1", "p2", "v")
    ts1.put("s2", "p", "v")
    ts1.put("s3", "p", "v")

    ts2 = TripleStore()
    ts2.put("ts2#s1", "p1", "v")
    ts2.put("ts2#s1", "p2", "v")
    ts2.put("ts2#s2", "p", "v")
    ts2.put("ts2#s3", "p", "v")

    ms.addStore(ts1)
    ms.addStore(ts2)

    print len(ts1.get())
    print len(ts2.get())
    print len(ms.get())


test_2()



