'''
Created on 25/lug/2013

@author: Davide Compagnin
'''

from decimal import Decimal

def nothing(_):
    pass

def default(t):
    return t.utilization()

def worst_fit(items, bins, capacity=Decimal(1), weight=default, misfit=nothing, empty_bin=list):
    sets = [empty_bin() for _ in xrange(0, bins)]
    sums = [Decimal(0) for _ in xrange(0, bins)]
    for x in items:
        c = weight(x)
        # pick the bin where the item will leave the most space
        # after placing it, aka the bin with the least sum
        candidates = [s for s in sums if s + c <= capacity]
        if candidates:
            # fits somewhere
            i = sums.index(min(candidates))
            sets[i] += [x]
            sums[i] += c
        else:
            misfit(x)
    return sets

def best_fit(items, bins, capacity=Decimal(1), weight=default, misfit=nothing, empty_bin=list):
    sets = [empty_bin()  for _ in xrange(0, bins)]
    sums = [Decimal(0) for _ in xrange(0, bins)]
    for x in items:
        c = weight(x)
        # find the first bin that is sufficiently large
        idxs = range(0, bins)
        idxs.sort(key=lambda i: sums[i], reverse=True)
        for i in idxs:
            if sums[i] + c <= capacity:
                sets[i] += [x]
                sums[i] += c
                break
        else:
            misfit(x)
    return sets

def first_fit(items, bins, capacity=Decimal(1), weight=default, misfit=nothing,
              empty_bin=list):
    sets = [empty_bin() for _ in xrange(0, bins)]
    sums = [Decimal(0) for _ in xrange(0, bins)]
    for x in items:
        c = weight(x)
        for i in xrange(0, bins):
            if sums[i] + c <= capacity:
                sets[i] += [x]
                sums[i] += c
                break
        else:
            misfit(x)

    return sets

def next_fit(items, bins, capacity=Decimal(1), weight=default, misfit=nothing,
             empty_bin=list):
    sets = [empty_bin() for _ in xrange(0, bins)]
    cur  = 0
    s  = Decimal(0)
    for x in items:
        c = weight(x)
        while s + c > capacity:
            s = Decimal(0)
            cur += 1
            if cur == bins:
                misfit(x)
                return sets
        sets[cur] += [x]
        s += c
    return sets