class RDFStore:

    def __init__(self):
	# indexed by [subject][property][value]
        self.localRDF = {}

        # indexed by [property][value][subject]
        self.localByProperty = {}

    def add(self, subject, property, value):
        if not subject in self.localRDF.keys():
            self.localRDF[subject] = {}

        if not property in self.localRDF[subject].keys():
            self.localRDF[subject][property] = {}

        self.localRDF[subject][property][value] = 1

        # add to byProperty
        if not property in self.localByProperty.keys():
            self.localByProperty[property] = {}

        if not value in self.localByProperty[property].keys():
            self.localByProperty[property][value] = {}

        self.localByProperty[property][value][subject] = 1

    def put(self, subject, property, value):
        self.remove(subject, property, value)
        self.add(subject, property, value)

    def get(self, subject=None, property=None, value=None):
        list = []

        if subject!=None:
            for s in self.localRDF.keys():
                if subject == None or subject == s:
                    for p in self.localRDF[s].keys():
                        if property == None or property == p:
                            for v in self.localRDF[s][p].keys():
                                if value == None or value == v:
                                    list.append((s, p, v))
        else:
            for p in self.localByProperty.keys():
                if property == None or property == p:
                    for v in self.localByProperty[p].keys():
                        if value == None or value == v:
                            for s in self.localByProperty[p][v].keys():
                                if subject == None or subject == s:
                                    list.append((s, p, v))
            
	return list

    def remove(self, subject, property, value):
        if subject in self.localRDF.keys() and property in self.localRDF[subject].keys():
            if self.localRDF[subject][property].has_key(value):
                del self.localRDF[subject][property][value]

        if property in self.localByProperty.keys() and value in self.localByProperty[property].keys():
            if self.localByProperty[property][value].has_key(subject):
                del self.localByProperty[property][value][subject]

    def removeAll(self, subject):
        list = self.get(subject, None, None)
        for item in list:
            self.remove(item[0], item[1], item[2])

