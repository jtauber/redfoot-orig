class RDFStore:

    def __init__(self):
	# indexed by [subject][property][value]
        self.spv = {}

        # indexed by [property][value][subject]
        self.pvs = {}

    def add(self, subject, property, value):
        if not subject in self.spv.keys():
            self.spv[subject] = {}

        if not property in self.spv[subject].keys():
            self.spv[subject][property] = {}

        self.spv[subject][property][value] = 1

        # add to byProperty
        if not property in self.pvs.keys():
            self.pvs[property] = {}

        if not value in self.pvs[property].keys():
            self.pvs[property][value] = {}

        self.pvs[property][value][subject] = 1

    def put(self, subject, property, value):
        self.remove(subject, property, value)
        self.add(subject, property, value)

    def get(self, subject=None, property=None, value=None):
        list = []

        if subject!=None:
            for s in self.spv.keys():
                if subject == None or subject == s:
                    for p in self.spv[s].keys():
                        if property == None or property == p:
                            for v in self.spv[s][p].keys():
                                if value == None or value == v:
                                    list.append((s, p, v))
        else:
            for p in self.pvs.keys():
                if property == None or property == p:
                    for v in self.pvs[p].keys():
                        if value == None or value == v:
                            for s in self.pvs[p][v].keys():
                                if subject == None or subject == s:
                                    list.append((s, p, v))
            
	return list

    def remove(self, subject, property, value):
        if subject in self.spv.keys() and property in self.spv[subject].keys():
            if self.spv[subject][property].has_key(value):
                del self.spv[subject][property][value]

        if property in self.pvs.keys() and value in self.pvs[property].keys():
            if self.pvs[property][value].has_key(subject):
                del self.pvs[property][value][subject]

    def removeAll(self, subject):
        list = self.get(subject, None, None)
        for item in list:
            self.remove(item[0], item[1], item[2])

