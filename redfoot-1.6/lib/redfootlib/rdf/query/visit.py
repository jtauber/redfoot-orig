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
