

class Statement:

    def __init__(self, s, p, o):
        self.subject = s
        self.predicate = p
        self.object = o


class StatementBuilder:
    
    def __init__(self):
        self.statement = None

    def accept(self, s, p, o):
        self.statement = Statement(s, p, o)

    def end(self):
        pass


def triple2statement(func):
    return lambda s, p, o, func=func: func(Statement(s, p, o))

def statement2triple(func):
    return lambda st, func=func: func(st.subject, st.predicate, st.object)


class ListBuilder:
    def __init__(self):
        self.list = []

    def accept(self, item):
        self.list.append(item)

    def filter(self, filter):
        list = []
        for item in self.list:
            if filter(item)==0:
                list.append(item)
        self.list = list
        
    def sort(self, comparator):
        self.list.sort(comparator)
        
    def visit(self, callback):        
        for item in self.list:
            callback(item)

    def end(self):
        pass

# TODO sort should perhaps be made more like ListBuilder
class SetBuilder:
    def __init__(self):
        self.dict = {}

    def accept(self, item):
        self.dict[item] = 1

    def end(self):
        pass

    def __getattr__(self, attr):
        if attr == "set":
            self.set = self.dict.keys()
            return self.set
        else:
            raise AttributeError

    def sort(self, func):
        d = {}
        for item in self.set:
            i = func(item)
            if not d.has_key(i):
                d[i] = []
            d[i].append(item)
        x = d.keys()
        x.sort()
        z = []
        for y in x:
            for m in d[y]:
              z.append(m)  
        return z
