from redfootlib.rdf.query.functors import *
from redfootlib.rdf.query.builders import *

from redfootlib.rdf.const import *

class Visit(object):
    
    def visit(self, callback, (subject, predicate, object)):
        """
        Visit all the triples that match the given triple mask by
        calling callback. The triple mask is a triple where any or all
        of subject, predicate, object may be ANY (AKA None).
        """
        for s, p, o in self.triples(subject, predicate, object):
            stop = callback(s, p, o)
            if stop:
                return stop

    def visit_typeless_resources(self, callback):
        self.visit_subjects(filter(s(callback), s(self.not_exists, TYPE, None)))

    def visit_by_type(self, callback, type, predicate, object):
        self.visit(filter(callback, s(self.is_of_type, type)), (None, predicate, object))

    # Alternative triple store implementations need not implement this
    # method as it can be implemented on top of the others. Although
    # it will likely be more efficient to implement at the triple
    # store level. 
    def visit_subjects(self, callback):
        """
        Experimental -- may change, depend on it at your own risk

        This method differs from visit(aSubject, ANY, ANY) in that it will only
        call the callback once per subject.
        """
        for s in self.subjects():
            callback(s, ANY, ANY)

    # TODO: currently goes into infinite loop if property loops back
    def visit_transitive(self, callback, root, property):
        self.visit(both(callback, o(callback_subject(self.visit_transitive, callback, property))),
                   (root, property, None))

    # TODO: currently goes into infinite loop if property loops back
    def visit_transitive_reverse(self, callback, root, property):
        self.visit(both(callback, s(callback_subject(self.visit_transitive_reverse, callback, property))),
                   (None, property, root))



############ Schema visit methods

    def visit_root_classes(self, callback):
        self.visit(filter(callback, s(self.not_exists, SUBCLASSOF, None)), (None, TYPE, CLASS))

    def visit_parent_types(self, callback, type):
        self.visit(callback, (type, SUBCLASSOF, None))

    def visit_possible_properties(self, callback, type):
        def f(superType, callback=callback, self=self):
            self.visit(s(callback), (None, DOMAIN, superType))
        self.visit_transitive(o(f), type, SUBCLASSOF)
        f(type)

    def visit_possible_properties_for_subject(self, callback, res):
        def f(type, callback=callback, self=self):
            self.visit_possible_properties(callback, type)
        self.visit(o(f), (res, TYPE, None))

    def visit_ranges(self, callback, property):
        self.visit(o(callback), (property, RANGE, None))

    # callback may be called more than once for the same possibleValue...
    # userof this method will have to remove duplicates
    def visit_possible_values(self, callback, property):
        def f(type, callback=callback, self=self):
            def e(type, callback=callback, self=self):
                self.visit(s(callback), (None, TYPE, type))
            self.visit_transitive_reverse(s(e), type, SUBCLASSOF)
            e(type)
        self.visit_ranges(f, property)

    def visit_resources_by_type(self, class_callback, instance_callback):
        b = SetBuilder()
        self.visit(o(b.accept), (None, TYPE, None))
        for type in b.set:
            if self.exists(None, TYPE, type):
                class_callback(type)
                self.visit(s(instance_callback), (None, TYPE, type))

    def visit_subclasses(self, class_start_callback, class_end_callback, instance_callback, root,
                         recurse=1, depth=0):
        class_start_callback(root, depth)

        def f(type,
              self=self, class_start_callback=class_start_callback,
              class_end_callback=class_end_callback, instance_callback=instance_callback, depth=depth):
            self.visit_subclasses(class_start_callback, class_end_callback, instance_callback,
                                  type, 1, depth + 1)

        def g(instance,
              depth=depth, instance_callback=instance_callback):
            instance_callback(instance, depth)

        def h(klass,
              depth=depth, class_start_callback=class_start_callback, class_end_callback=class_end_callback):
            class_start_callback(klass, depth + 1)
            class_end_callback(klass, depth + 1)

        if recurse:
            self.visit(s(f), (None, SUBCLASSOF, root))
        else:
            self.visit(s(h), (None, SUBCLASSOF, root))

        self.visit(s(g), (None, TYPE, root))

        class_end_callback(root, depth)

        

