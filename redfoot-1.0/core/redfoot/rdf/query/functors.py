
def s(func):
    return lambda s, p, o, func=func: func(s)

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

def filter(callback, condition):
    return lambda s, p, o, callback=callback, condition=condition: condition(s, p, o) and callback(s, p, o)

def subject(func, *args):
    return lambda s, p, o, func=func, args=args: apply(func, (s,) + args)

def not_subject(func, *args):
    return lambda s, p, o, func=func, args=args: not apply(func, (s,) + args)

# TODO what to call this?
def callback_subject(func, callback, *args):
    return lambda s, func=func, callback=callback, args=args: apply(func, (callback, s) + args)