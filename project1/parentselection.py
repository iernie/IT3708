from __future__ import division
from abc import ABCMeta, abstractmethod, abstractproperty
import main

from random import randint, random, shuffle

class ParentSelection(object):
    __metaclass__ = ABCMeta

    def __iter__(self):
        return self

    def next(self):
        p1 = None
        p2 = None
        r1 = random()
        r2 = random()
        for a,x in self.h:
            if r1 < a:
                p1 = x
                break
        for a,x in self.h:
            if r2 < a:
                p2 = x
                break
        return p1,p2

class NormalizedRoulette(ParentSelection):

    def __init__(self, adults):
        ft = [x.fitness for x in adults]
        s = sum(ft, 0.0)
        ft[0] /= s
        for i in range(1,len(ft)):
            ft[i] /= s
            ft[i] += ft[i-1]
        self.h = zip(ft,adults)

class SigmaScaling(ParentSelection):

    def __init__(self, adults):
        ft = [x.fitness for x in adults]
        sd = 2*standard_deviation(ft)
        if sd == 0:
            self.h = [1]*len(adults)
        else:
            avg = average(ft)
            self.h = []
            for a in adults:
                self.h.append((1+(a.fitness-avg)/sd))
        s = sum(self.h,0.0)
        self.h[0] /= s
        for i in range(1, len(self.h)):
            self.h[i] /= s
            self.h[i] += self.h[i-1]
        self.h = zip(self.h, adults)

def TournamentSelectionFactory(k, eps):
    class TournamentSelection(ParentSelection):
        def __init__(self, adults):
            self.adults = adults
        
        def nextp(self):
            tournament = list(self.adults) 
            shuffle(tournament)
            tournament = tournament[:k]
            cr = random()
            if cr < eps:
                return tournament[0]
            else:
                return max(tournament, key=lambda x: x.fitness)
        
        def next(self):
            return self.nextp(), self.nextp()
    return TournamentSelection

def RankSelectionFactory(max_ft, min_ft):
    class RankSelection(ParentSelection):
        def __init__(self, adults):
            self.adults = adults
            self.h = []
            for a in adults:
                self.h.append((min_ft+(max_ft-min_ft)*(self.rank(a)-1/len(adults)-1)))
            self.h = zip(self.h, adults)

        def rank(self, individual):
            adults_sorted = sorted(self.adults, key=lambda x: x.fitness)
            return adults_sorted.index(individual) + 1
    return RankSelection