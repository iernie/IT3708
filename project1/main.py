from __future__ import division

from abc import ABCMeta, abstractmethod, abstractproperty
from random import randint

import pylab as p

def average(values):
    return sum(values, 0.0) / len(values)


class EA(object):

    def __init__(self, population, crossover,
            mutation, genotype, adult_selection, **kwargs):
        self.individuals = []
        for i in xrange(population):
            self.individuals.append(genotype(None, **kwargs))
        self.crossover = crossover
        self.mutation = mutation
        self.adult_selection = adult_selection

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

        p.plot(maxs)
        p.plot(avgs)
        p.show()
    


class Genotype(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def develop(self): pass

    @abstractmethod
    def crossover(self): pass

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
        self.phenotype = phenotype

    def crossover(self, other):
        assert isinstance(other, BitVectorGenotype)
        assert len(self.vector) == len(other.vector)
        i = randint(0,len(self.vector))
        if randint(0,1) == 0:
            return other.vector[:i] + self.vector[i:]
        else:
            return self.vector[:i] + other.vector[i:]

    def mutate(self):
        i = randint(0,len(self.vector))
        h = self.vector
        h[i] = (h[i] + 1)&1
        return h

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
    pass

if __name__ == '__main__':
    asa = A_I()

    ea = EA(20, 0.5, 0.1, BitVectorGenotype, length=20, 
            adult_selection=asa, phenotype=OneMaxPhenotype)
    ea.loop(100)
