from redfoot.rdf import objects

def run():
    passed = 0
    
    u1 = '1'
    u2 = unicode('2')
    u3 = '12'
    a = objects.resource(u1+u2)
    b = objects.resource(u3)

    if a==b:
        passed = passed + 1

    if id(a)==id(b):
        passed = passed + 1

    a = objects.literal(u1+u2)
    b = objects.literal(u3)

    if a==b:
        passed = passed + 1

    # TODO: we may want to intern the keys for resource and literal
    # dictionaries. As I think there is a performance gain. But have
    # also read that intern-ed string are immortal and never get
    # garbage collected -- maybe this will change in a future version
    # of python.
    
    return (passed==3, '')

