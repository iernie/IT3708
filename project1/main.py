from __future__ import division

from abc import ABCMeta, abstractmethod, abstractproperty
from random import randint, random

import pylab as p

def average(values):
    return sum(values, 0.0) / len(values)


class EA(object):

    def __init__(self, population, crossover,
            mutation, genotype, adult_selection,
            parent_selection, **kwargs):
        self.individuals = []
        for i in xrange(population):
            self.individuals.append(genotype(None, **kwargs))
        self.crossover = crossover
        self.mutation = mutation
        self.adult_selection = adult_selection
        self.parent_selection = parent_selection
        self.population = population

    def loop(self, generations):
        maxs = []
        avgs = []

        for i in xrange(generations):
            pts = [x.develop(i) for x in self.individuals]
            fitness = [x.fitness for x in pts]
            maxs.append(max(fitness))
            avgs.append(average(fitness))

            adults = self.adult_selection.select(pts)
            retain = self.adult_selection.retain(adults)

            children = []
            i = self.population - len(retain)
            for p1,p2 in self.parent_selection(adults):
                ## reproduction
                cr = random()
                cg = None
                if cr < self.crossover:
                    cg = p1.genotype.crossover(p2.genotype)
                else:
                    cr = random()
                    if cr < 0.5:
                        cg = p1.genotype
                    else:
                        cg = p2.genotype
                cr = random()
                if cr < self.mutation:
                    cg.mutate()

                children.append(cg)

                i -= 1
                if i <= 0: break
            
            self.individuals = children + [x.genotype for x in retain]
            

        p.plot(maxs)
        p.plot(avgs)
        p.show()
    


class Genotype(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def develop(self): pass

    @abstractmethod
    def crossover(self,other): pass

    @abstractmethod
    def mutate(self): pass

class BitVectorGenotype(Genotype):

    def __init__(self, vector, length, phenotype):
        if vector == None:
            self.vector = []
            for i in range(length):
                self.vector.append(randint(0,1))
        else:
            self.vector = vector
        self.length = length
        self.phenotype = phenotype

    def crossover(self, other):
        assert isinstance(other, BitVectorGenotype)
        assert len(self.vector) == len(other.vector)
        i = randint(0,len(self.vector))
        if randint(0,1) == 0:
            return BitVectorGenotype(
                    other.vector[:i] + self.vector[i:],
                    self.length, 
                    self.phenotype)
        else:
            return BitVectorGenotype(
                    self.vector[:i] + other.vector[i:],
                    self.length,
                    self.phenotype)

    def mutate(self):
        i = randint(0,len(self.vector)-1)
        h = self.vector
        h[i] = (h[i] + 1)&1
        return BitVectorGenotype(h,
                self.length,
                self.phenotype)

    def develop(self, i):
        return self.phenotype(self, i)

class Phenotype(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def fitness(self): pass

class OneMaxPhenotype(Phenotype):

    def __init__(self, genotype, generation):
        assert isinstance(genotype, BitVectorGenotype)
        self.genotype = genotype
        self.generation = generation

    @property
    def fitness(self):
        return average(self.genotype.vector)

class AdultSelection(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def select(self, pool): pass

    @abstractmethod
    def retain(self, pool): pass


class A_I(AdultSelection):
    # Full Generational Replacement
    def select(self, pool):
        return pool
    def retain(self, pool):
        return []


class A_II(AdultSelection):
    # Over-production
    pass

class A_III(AdultSelection):
    # Generational Mixing
    pass


class ParentSelection(object):
    __metaclass__ = ABCMeta

class NormalizedRoulette(ParentSelection):

    def __init__(self, adults):
        ft = [x.fitness for x in adults]
        s = sum(ft, 0.0)
        ft[0] /= s
        for i in range(1,len(ft)):
            ft[i] /= s
            ft[i] += ft[i-1]
        self.h = zip(ft,adults)

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

        

if __name__ == '__main__':
    asa = A_I()

    ea = EA(20, 0.9, 0.05, BitVectorGenotype, length=20, 
            adult_selection=asa, parent_selection=NormalizedRoulette, phenotype=OneMaxPhenotype)
    ea.loop(100)
