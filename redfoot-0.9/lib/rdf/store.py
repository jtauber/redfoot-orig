# $Header$

def literal(str):
    return "^"+str

def is_literal(str):
    return str[0]=="^"

class TripleStore:

    def __init__(self):
	# indexed by [subject][predicate][object]
        self.spo = {}

        # indexed by [predicate][object][subject]
        self.pos = {}

    def add(self, subject, predicate, object):
        # spo
        if not self.spo.has_key(subject):
            self.spo[subject] = {}

        if not self.spo[subject].has_key(predicate):
            self.spo[subject][predicate] = {}

        self.spo[subject][predicate][object] = 1

        # pos
        if not self.pos.has_key(predicate):
            self.pos[predicate] = {}

        if not self.pos[predicate].has_key(object):
            self.pos[predicate][object] = {}

        self.pos[predicate][object][subject] = 1

    def get(self, subject=None, predicate=None, object=None):
        class Visitor:
            def __init__(self):
                self.list = []

            def callback(self, subject, predicate, object):
                self.list.append((subject, predicate, object))

        visitor = Visitor()
        self.visit(visitor.callback, subject, predicate, object)

	return visitor.list

    def remove(self, subject=None, predicate=None, object=None):
        def callback(subject, predicate, object, self=self):
            del self.spo[subject][predicate][object]
            del self.pos[predicate][object][subject]

        self.visit(callback, subject, predicate, object)

    def visit(self, callback, subject=None, predicate=None, object=None):
        if subject!=None: # subject is given
            if self.spo.has_key(subject):
                if predicate!=None: # subject+predicate is given
                    if self.spo[subject].has_key(predicate):
                        if object!=None: # subject+predicate+object is given
                            if self.spo[subject][predicate].has_key(object):
                                callback(subject, predicate, object)
                            else: # given object not found
                                pass
                        else: # subject+predicate is given, object unbound
                            for o in self.spo[subject][predicate].keys():
                                callback(subject, predicate, o)
                    else: # given predicate not found
                        pass
                else: # subject given, predicate unbound
                    for p in self.spo[subject].keys():
                        if object!=None: # object is given
                            if self.spo[subject][p].has_key(object):
                                callback(subject, p, object)
                            else: # given object not found
                                pass
                        else: # object unbound
                            for o in self.spo[subject][p].keys():
                                callback(subject, p, o)
            else: # given subject not found
                pass
        elif predicate!=None: # predicate is given, subject unbound
            if self.pos.has_key(predicate):
                if object!=None: # predicate+object is given, subject unbound
                    if self.pos[predicate].has_key(object):
                        for s in self.pos[predicate][object].keys():
                            callback(s, predicate, object)
                    else: # given object not found
                        pass
                else: # predicate is given, object+subject unbound
                    for o in self.pos[predicate].keys():
                        for s in self.pos[predicate][o].keys():
                            callback(s, predicate, o)
        elif object!=None: # object is given, subject+predicate unbound
            for p in self.pos.keys():
                if self.pos[p].has_key(object):
                    for s in self.pos[p][object]:
                        callback(s, p, object)
                else: # given object not found
                    pass
        else: # subject+predicate+object unbound
            for s in self.spo.keys():
                for p in self.spo[s].keys():
                    for o in self.spo[s][p].keys():
                        callback(s, p, o)
                    

#~ $Log$
#~ Revision 4.3  2000/12/03 21:21:49  jtauber
#~ removed put; refactored remove to use callback function
#~
#~ Revision 4.2  2000/12/03 20:49:38  jtauber
#~ refactored+documented visit function
#~
#~ Revision 4.1  2000/12/03 20:17:40  jtauber
#~ changed property/value to predicate/object
#~
#~ Revision 4.0  2000/11/06 15:57:33  eikeon
#~ VERSION 4.0
#~
#~ Revision 3.1  2000/11/02 21:48:27  eikeon
#~ removed old log messages
#~
# Revision 3.0  2000/10/27 01:23:10  eikeon
# bump-ing version to 3.0
