from time import mktime, time, gmtime, timezone, altzone, daylight

def date_time(t=None):
    """http://www.w3.org/TR/NOTE-datetime ex: 1997-07-16T19:20:30Z"""
    t = t or time()    
    year, month, day, hh, mm, ss, wd, y, z = gmtime(t)
    s = "%0004d-%02d-%02dT%02d:%02d:%02dZ" % ( year, month, day, hh, mm, ss)
    return s

def parse_date_time(val):
    ymd, hms = val.split("T")
    year, month, day = ymd.split("-")
    hour, minute, second = hms[:-1].split(":")
    
    t = mktime((int(year), int(month), int(day), int(hour),
                        int(minute), int(second), 0, 0, -1))

    if daylight:
        t = t - altzone
    else:
        t = t - timezone

    return t

#t1 = time()
#print t1, date_time(t1)
#t = parse_date_time(date_time(t1))
#print t, date_time(t)
