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
                    

#~ $Log$
#~ Revision 3.1  2000/11/02 21:48:27  eikeon
#~ removed old log messages
#~
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
