# $Header$

class TripleStore:

    def __init__(self):
	# indexed by [subject][property][value]
        self.spv = {}

        # indexed by [property][value][subject]
        self.pvs = {}

    def add(self, subject, property, value):
        if not self.spv.has_key(subject):
            self.spv[subject] = {}

        if not self.spv[subject].has_key(property):
            self.spv[subject][property] = {}

        self.spv[subject][property][value] = 1

        # add to byProperty
        if not self.pvs.has_key(property):
            self.pvs[property] = {}

        if not self.pvs[property].has_key(value):
            self.pvs[property][value] = {}

        self.pvs[property][value][subject] = 1

    def put(self, subject, property, value):
        self.remove(subject, property, value)
        self.add(subject, property, value)

    def get(self, subject=None, property=None, value=None):
        class Visitor:
            def __init__(self):
                self.list = []

            def callback(self, subject, property, value):
                self.list.append((subject, property, value))

        visitor = Visitor()
        self.visit(visitor.callback, subject, property, value)

	return visitor.list

    def remove(self, subject=None, property=None, value=None):
        class Visitor:
            def __init__(self, store):
                self.store = store

            def callback(self, subject, property, value):
                del self.store.spv[subject][property][value]
                del self.store.pvs[property][value][subject]

        visitor = Visitor(self)
        self.visit(visitor.callback, subject, property, value)

    def visit(self, callback, subject=None, property=None, value=None):
        if subject!=None:
            if self.spv.has_key(subject):
                if property!=None:
                    if self.spv[subject].has_key(property):
                        if value!=None:
                            if self.spv[subject][property].has_key(value):
                                callback(subject, property, value)
                        else:
                            for v in self.spv[subject][property].keys():
                                callback(subject, property, v)
                else:
                    for p in self.spv[subject].keys():
                        self.visit(callback, subject, p, value) # recurse for now
        else:
            if property!=None:
                if self.pvs.has_key(property):
                    if value!=None:
                        if self.pvs[property].has_key(value):
                            for s in self.pvs[property][value].keys():
                                callback(s, property, value)
                    else:
                        for v in self.pvs[property].keys():
                            for s in self.pvs[property][v].keys():
                                callback(s, property, v)
            else:
                if value!=None:
                    for p in self.pvs.keys():
                        if self.pvs[p].has_key(value):
                            for s in self.pvs[p][value]:
                                callback(s, p, value)
                else:
                    for s in self.spv.keys():
                        for p in self.spv[s].keys():
                            for v in self.spv[s][p].keys():
                                callback(s, p, v)
                    

# $Log$
# Revision 2.0  2000/10/14 01:14:04  jtauber
# next version
#
# Revision 1.18  2000/10/08 04:49:11  eikeon
# reimplemented visit method to be much more efficient... was just a first pass implementation before ;(
#
# Revision 1.17  2000/10/06 03:07:56  eikeon
# removed pesky ^M^Ms
#
# Revision 1.16  2000/10/03 06:01:50  jtauber
# moved MultiStore and StoreNode to rednode.py
#
# Revision 1.15  2000/10/01 16:42:44  eikeon
# added a preCacheRemoteStores method that looks for and wholesale caches any RemoteStores if finds
#
# Revision 1.14  2000/10/01 07:41:09  eikeon
# fixed missing imports etc from previous premature checkin ;(
#
# Revision 1.13  2000/10/01 07:24:26  eikeon
# moved loading of the rdf-schema and rdf-syntax into StoreNode
#
# Revision 1.12  2000/10/01 03:58:10  eikeon
# fixed up all the places where I put CVS keywords as keywords in omments... duh
#
# Revision 1.11  2000/10/01 02:23:06  eikeon
# Changing Id to Header
#
# Revision 1.10  2000/10/01 02:18:05  eikeon
# MultiStore now has both visit and get methods; Added a StoreNode class; added Header and Log CVS keywords

