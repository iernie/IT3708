from __future__ import division
from math import sqrt
import getopt
import sys
from random import randint, random, shuffle

import matplotlib.pyplot as plt
import adultselection as adsel
import genotype as geno
import parentselection as parsel
import phenotype as pheno

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
        return adsel.A_I(population)
    elif adultselect == "A_II":
        return adsel.A_II(population, fitchildren)
    elif adultselect == "A_III":
        return adsel.A_III(population, fitchildren)

def get_parent_selection(parentselect, k, eps, max_ft, min_ft):
    if parentselect == "P_I":
        return parsel.NormalizedRoulette
    elif parentselect == "P_II":
        return parsel.SigmaScaling
    elif parentselect == "P_III":
        return parsel.TournamentSelectionFactory(k, eps)
    elif parentselect == "P_IV":
        return parsel.RankSelectionFactory(max_ft, min_ft)

class EA(object):

    def __init__(self, population, crossover,
            genotype, adult_selection,
            parent_selection, figure, **kwargs):
        self.individuals = []
        for i in xrange(population):
            self.individuals.append(genotype(None, **kwargs))
        self.crossover = crossover
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
                cg = p1.genotype.copy()
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
            avgs.append(average(fitness))
            print "Winner",i,max(self.pts, key=lambda x: x.fitness), maxs[-1], len(self.pts), avgs[-1]

            if doentropy:
                strategy_entropies.append(average([x.strategy_entropy for x in self.pts]))


            adults = self.adult_selection.select(self.pts)
            retain = self.adult_selection.retain(adults)
            
            #b=max(retain, key=lambda x: x.fitness)
            #print "%.5f"%b.fitness, b.genotype.vector

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
            
        ext = ".png"

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(maxs)
        ax.plot(sds)
        ax.plot(avgs)
        fig.savefig(self.figure+ext)

        if strategy_entropies:
            fig2 = plt.figure()
            ax = fig2.add_subplot(111)
            ax.plot(strategy_entropies)
            fig2.savefig(self.figure+'_entropies'+ext)

        print max(maxs), maxs.index(max(maxs))
        #p.plot(maxs)
        #p.plot(avgs)
        #p.save("figure.png")

if __name__ == '__main__':
    #Default values
    population = 500
    generations = 50
    bvl = 33
    fitchildren = 1000
    adultselect = "A_III"
    parentselect = "P_II"
    phenotype = pheno.IzhikevichPhenotype
    k = 20
    eps = 0.05
    max_ft = 1.5
    min_ft = 0.5
    crossover = 0.95
    mutation = 0.25
    figure = "figure"
    Rf = 0.5
    Lf = 0.5
    sdm = 1
    td = 1

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
                    'figure=',
                    'rf=',
                    'lf=',
                    'sdm=',
                    'td='
                    ])
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
                phenotype = eval("pheno."+a)
            except:
                print "You don't exist. Go away!"
                sys.exit(-1)

        if o in ('--crossover'):
            crossover = float(a)

        if o in ('--mutation'):
            mutation = float(a)

        if o in ('--figure'):
            figure = str(a)

        if o in ('--rf'):
            Rf = float(a)

        if o in ('--lf'):
            Lf = float(a)

        if o in ('--sdm'):
            sdm = int(a)

        if o in ('--td'):
            td = int(a)

    ea = EA(fitchildren, crossover, 
            geno.BitVectorGenotype,
            figure=figure,
            length=bvl,
            Rf=Rf,
            Lf=Lf,
            adult_selection=get_adult_selection(adultselect, population, fitchildren),
            parent_selection=get_parent_selection(parentselect, k, eps, max_ft, min_ft),
            phenotype=phenotype,
            sdm=sdm,
            mutation=mutation,
            td=td)
    ea.loop(generations)
