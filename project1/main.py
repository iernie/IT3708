from __future__ import division

from abc import ABCMeta, abstractmethod, abstractproperty
from random import randint, random, shuffle
from math import sqrt
import getopt
import sys

#import pylab as p
import matplotlib.pyplot as plt
import part1b

def average(values):
    return sum(values, 0.0) / len(values)

def standard_deviation(values):
    avg = average(values)
    tmp = 0
    for f in values:
        tmp += (f-avg)**2
    tmp /= len(values)
    return sqrt(tmp)

def get_adult_selection(adultselect, population, fitchildren):
    if adultselect == "A_I":
        return A_I(population)
    elif adultselect == "A_II":
        return A_II(population, fitchildren)
    elif adultselect == "A_III":
        return A_III(population, fitchildren)

def get_parent_selection(parentselect, k, eps, max_ft, min_ft):
    if parentselect == "normalized":
        return NormalizedRoulette
    elif parentselect == "sigma":
        return SigmaScaling
    elif parentselect == "tournament":
        return TournamentSelectionFactory(k, eps)
    elif parentselect == "rank":
        return RankSelectionFactory(max_ft, min_ft)

class EA(object):

    def __init__(self, population, crossover,
            mutation, genotype, adult_selection,
            parent_selection, figure, **kwargs):
        self.individuals = []
        for i in xrange(population):
            self.individuals.append(genotype(None, **kwargs))
        self.crossover = crossover
        self.mutation = mutation
        self.adult_selection = adult_selection
        self.parent_selection = parent_selection
        self.population = population
        self.pts = []
        self.genotype = genotype
        self.figure = figure

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
        sds = []  # standard deviations
        strategy_entropies = []

        if hasattr(self.individuals[0].phenotype, 'strategy_entropy'):
            doentropy = True
        else:
            doentropy = False

        for i in xrange(generations):
            self.pts = [x.develop(self) for x in self.individuals]
            fitness = [x.fitness for x in self.pts]
            maxs.append(max(fitness))
            sds.append(standard_deviation(fitness))
            print "Winner",i,max(self.pts, key=lambda x: x.fitness), maxs[-1]
            avgs.append(average(fitness))
            if doentropy:
                strategy_entropies.append(average([x.strategy_entropy for x in self.pts]))


            adults = self.adult_selection.select(self.pts)
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
            

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(maxs)
        ax.plot(sds)
        ax.plot(avgs)
        fig.savefig(self.figure+".eps")

        if strategy_entropies:
            fig2 = plt.figure()
            ax = fig2.add_subplot(111)
            ax.plot(strategy_entropies)
            fig2.savefig(self.figure+'_entropies.eps')
        #p.plot(maxs)
        #p.plot(avgs)
        #p.save("figure.png")
    


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

    def __repr__(self):
        return "<BitVectorGenotype()>"

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

    def __repr__(self):
        s = "<OneMaxPhenotype("
        s += "".join(str(x) for x in self.genotype.vector)
        s += ")"
        return s

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

if __name__ == '__main__':
    #Default values
    population = 30
    generations = 100
    bvl = 40
    fitchildren = 40
    adultselect = "A_III"
    parentselect = "rank"
    phenotype = OneMaxPhenotype
    k = 20
    eps = 0.05
    max_ft = 1.5
    min_ft = 0.5
    crossover = 0.9
    mutation = 0.1
    figure = "figure"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "",
                ['population=',
                    'generations=',
                    'bvl=',
                    'fitchildren=',
                    'adultselect=',
                    'parentselect=',
                    'min=',
                    'max=', 
                    'k=', 
                    'e=',
                    'phenotype=',
                    'crossover=',
                    'mutation=',
                    'figure='])
    except getopt.GetoptError:
        print "Available options: --population, --generations, --bvl, --fitchildren, --adultselect, --parentselect, --k, --e, --min, --max, --phenotype, --crossover, --mutation, --figure"
        sys.exit()
    
    for o, a in opts:
        #Set population size
        if o in ('--population'):
            population = int(a)

        #Set number of generations
        if o in ('--generations'):
            generations = int(a)

        #Set bit vector length
        if o in ('--bvl'):
            bvl = int(a)

        #Set number of children that are allowed to grow up
        if o in ('--fitchildren'):
            fitchildren = int(a)

        #Set the adult selection mechanism
        if o in ('--adultselect'):
            adultselect = str(a)

        #Set the parent selection mechanism
        if o in ('--parentselect'):
            parentselect = str(a)

        if o in ('--k'):
            k = int(a)

        if o in ('--e'):
            eps = float(a)

        if o in ('--min'):
            min_ft = float(a)

        if o in ('--max'):
            max_ft = float(a)

        if o in ('--phenotype'):
            try:
                phenotype = eval(a)
            except:
                print "You don't exist. Go away!"
                sys.exit(-1)

        if o in ('--crossover'):
            crossover = float(a)

        if o in ('--mutation'):
            mutation = float(a)

        if o in ('--figure'):
            figure = str(a)

    ea = EA(fitchildren, crossover, mutation, BitVectorGenotype,
            figure=figure,
            length=bvl, 
            adult_selection=get_adult_selection(adultselect, population, fitchildren),
            parent_selection=get_parent_selection(parentselect, k, eps, max_ft, min_ft),
            phenotype=phenotype)
    ea.loop(generations)
