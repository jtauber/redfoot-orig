
class Statement:

    def __init__(self, s, p, o):
        self.subject = s
        self.predicate = p
        self.object = o


def triple2statement(func):
    return lambda s, p, o, func=func: func(Statement(s, p, o))

def statement2triple(func):
    return lambda st, func=func: func(st.subject, st.predicate, st.object)


class ItemBuilder:
    def __init__(self):
        self.item = None

    def accept(self, item):
        self.item = item


class ListBuilder:
    def __init__(self):
        self.list = []

    def accept(self, item):
        self.list.append(item)

    def filter(self, filter):
        list = []
        for item in self.list:
            if filter(item):
                list.append(item)
        self.list = list
        
    def sort(self, comparator):
        self.list.sort(comparator)
        
    def visit(self, callback):        
        for item in self.list:
            callback(item)


class SetBuilder:
    def __init__(self):
        self.dict = {}

    def accept(self, item):
        self.dict[item] = 1

    def __getattr__(self, attr):
        if attr == "set":
            self.set = self.dict.keys()
            return self.set
        else:
            raise AttributeError

    def filter(self, filter):
        set = []
        for item in self.set:
            if filter(item):
                set.append(item)
        self.set = set

    def sort(self, comparator):
        self.set.sort(comparator)

    def visit(self, callback):
        for item in self.set:
            callback(item)
