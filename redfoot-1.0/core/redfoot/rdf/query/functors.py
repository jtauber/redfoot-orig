
def s(func, *args):
    return lambda s, p, o, func=func, args=args: apply(func, (s,) + args)

def o(func):
    return lambda s, p, o, func=func: func(o)

def so(func):
    return lambda s, p, o, func=func: func(s, o)

def po(func):
    return lambda s, p, o, func=func: func(p, o)

def both(func1, func2):
    return lambda s, p, o, func1=func1, func2=func2: func1(s, p, o) or func2(s, p, o)

def first(func):
    return lambda s, p, o, func=func: func(s, p, o) or 1

# TODO: generalize me:
#   convert to class with __call__ and change s, p, o to *args
#def filter(callback, condition):
#    return lambda s, p, o, callback=callback, condition=condition: condition(s, p, o) and callback(s, p, o)

class filter:
    def __init__(self, callback, condition):
        self.callback = callback
        self.condition = condition

    def __call__(self, *args):
        if apply(self.condition, args):
            apply(self.callback, args)


# TODO what to call this?
def callback_subject(func, callback, *args):
    return lambda s, func=func, callback=callback, args=args: apply(func, (callback, s) + args)

class sort:
    def __init__(self, comparator, visit):
        self.visit = visit        
        self.comparator = comparator
        self.list = []

    def inner_callback(self, *args):
        self.list.append(args)
        
    def __call__(self, callback, *args):
        self.visit(self.inner_callback, *args)
        self.finished(callback)
        
    def finished(self, callback):
        list = self.list
        list.sort(self.comparator)
        for args in list:
            apply(callback, args)


class remove_duplicates:
    def __init__(self, callback, adapter):
        self.callback = callback
        self.adapter = adapter
        self.items = []

    def __call__(self, *args):
        items = self.items
        item = self.adapter(args)
        if item not in items:
            items.append(item)
            apply(self.callback, args)
