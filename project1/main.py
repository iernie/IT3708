from __future__ import division

from abc import ABCMeta, abstractmethod, abstractproperty
from random import randint, random, shuffle
from math import sqrt
import getopt

import pylab as p

def average(values):
    return sum(values, 0.0) / len(values)

def standard_deviation(values):
    avg = average(values)
    tmp = 0
    for f in values:
        tmp += (f-avg)**2
    tmp /= len(values)
    return sqrt(tmp)

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
        def reproduce(p1,p2):
            cr = random()
            cg = None
            if cr < self.crossover:
                cg = p1.genotype.crossover(p2.genotype) 
            else:
                cg = p1.genotype
            cr = random()
            if cr < self.mutation:
                cg.mutate()
            return cg
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
            i = self.adult_selection.produce()
            for p1,p2 in self.parent_selection(adults):
                ## reproduction
                children.append(reproduce(p1,p2))
                i -= 1
                if i <= 0: break
                children.append(reproduce(p2,p1))
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

    @abstractmethod
    def produce(self): pass


class A_I(AdultSelection):
    # Full Generational Replacement
    def __init__(self, population):
        self.population = population

    def select(self, pool):
        return pool

    def retain(self, pool):
        return []

    def produce(self):
        return self.population


class A_II(AdultSelection):
    # Over-production
    def __init__(self, no_adults, no_children):
        self.no_adults = no_adults
        self.no_children = no_children

    def select(self, pool):
        return sorted(pool, key=lambda x: x.fitness, reverse=True)[:self.no_adults]

    def retain(self, pool):
        return []

    def produce(self):
        return self.no_children

class A_III(AdultSelection):
    # Generational Mixing
    def __init__(self, no_adults, no_children):
        self.no_adults = no_adults
        self.no_children = no_children
    
    def select(self, pool):
        return sorted(pool, key=lambda x: x.fitness, reverse=True)[:self.no_adults]
    
    def retain(self, pool):
        return pool
    
    def produce(self):
        return self.no_children


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
        K = k
        e = eps
        def __init__(self, adults):
            self.adults = adults
        
        def nextp(self):
            tournament = list(self.adults) 
            shuffle(tournament)
            tournament = tournament[:self.K]
            cr = random()
            if cr < self.e:
                return tournament[0]
            else:
                return max(tournament, key=lambda x: x.fitness)
        
        def next(self):
            return self.nextp(), self.nextp()
    return TournamentSelection

def RankSelectionFactory(max_fta, min_fta):
    class RankSelection(ParentSelection):
        max_ft = max_fta
        min_ft = min_fta
        def __init__(self, adults):
            self.adults = adults
            self.h = []
            for a in adults:
                self.h.append((self.min_ft+(self.max_ft-self.min_ft)*(self.rank(a)-1/len(adults)-1)))
            self.h = zip(self.h, adults)

        def rank(self, individual):
            adults_sorted = sorted(self.adults, key=lambda x: x.fitness)
            return adults_sorted.index(individual) + 1
    return RankSelection

if __name__ == '__main__':
    #Default values
    population = 30
    generations = 100

    try:
        opts, args = getopt.getopt(sys.argv[1:], "pg", ['population', 'generations'])
    except getopt.GetoptError:
        print "Available options: --population, --generations"
        sys.exit()
    
    for o, a in opts:
        #Set population size
        if o in ('--population'):
            population = a

        #Set number of generations
        if o in ('--generations'):
            generations = a

    asa = A_III(population, 40)

    ea = EA(40, 0.9, 0.1, BitVectorGenotype, length=40, 
            adult_selection=asa, parent_selection=RankSelectionFactory(1.5,0.5), phenotype=OneMaxPhenotype)
    ea.loop(generations)
