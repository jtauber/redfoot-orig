from time import time, gmtime

class URIGenerator:
    def __init__(self):
        self.sn = 0
        self.time_path = None

    def get_sn(self):
        self.sn = self.sn + 1
        return self.sn

    def date_time_path(self, t=None):
        """."""
        
        if t==None:
            t = time()

        year, month, day, hh, mm, ss, wd, y, z = gmtime(t)           
        time_path = "%0004d/%02d/%02d/T%02d/%02d/%02dZ" % ( year, month, day, hh, mm, ss)

        if time_path==self.time_path:
            sn = self.sn
            self.sn = sn + 1
        else:
            self.sn = 0
            self.time_path = time_path


        s = self.time_path + "%.004d" % self.sn
        return s

generator = URIGenerator()
generate_uri = generator.date_time_path
