from itertools import groupby


def unique(l):
    l.sort()
    return list(k for k, _ in groupby(l))


