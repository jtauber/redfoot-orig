
from redfoot.rdf.query.functors import *
from redfoot.rdf.query.core import *
from redfoot.rdf.query.builders import *

from redfoot.rdf.const import *


class SchemaQuery(Query):

    # TODO: should we have a version of this that answers for subclasses too?
    def is_of_type(self, res, type):
        return self.exists(res, TYPE, type)

    def visit_typeless_resources(self, callback):
        self.visit_subjects(filter(s(callback), s(self.not_exists, TYPE, None)))

    def visit_by_type(self, callback, type, predicate, object):
        self.visit(filter(callback, s(self.is_of_type, type)), (None, predicate, object))

    # TODO: method to return all labels
    def label(self, subject, default=None):
        b = ItemBuilder()
        self.visit(first(o(b.accept)), (subject, LABEL, None))
        if b.item == None:
            first_label = None
        else:
            first_label = b.item
        if first_label:
            return first_label
        elif default != None:
            return default
        else:
            return subject

    def comment(self, subject, default=None):
        b = ItemBuilder()
        self.visit(first(o(b.accept)), (subject, COMMENT, None))
        if b.item == None:
            first_comment = None
        else:
            first_comment = b.item
        if first_comment:
            return first_comment
        elif default != None:
            return default
        else:
            return self.label(subject)

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

    # REIFICATION
    def visit_reified_statements_about_subject(self, callback, subject):
        def f(statement_uri, subject=subject, self=self, callback=callback):
            callback(statement_uri, subject, self.get_first(statement_uri, PREDICATE, None).object, self.get_first(statement_uri, OBJECT, None).object)
        self.visit_by_type(s(f), STATEMENT, SUBJECT, subject)
