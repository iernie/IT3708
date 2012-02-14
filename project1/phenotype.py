from __future__ import division
from abc import ABCMeta, abstractmethod, abstractproperty
import main
import genotype as geno
import math

from random import randint, random, shuffle

def average(values):
    return sum(values, 0.0) / len(values)

def simulate_war(this, others, Rf, Lf):
    wins = 0
    length = len(this.strategy)
    for os in others:
        if os == this: continue
        iwin = 0
        assert len(this.strategy) == len(os.strategy)
        mytroops = [float(x) for x in this.strategy]
        ostroops = [float(x) for x in os.strategy]
        my_sf = 1.0 # strength factor
        os_sf = 1.0
        for i in range(len(mytroops)):
            if my_sf * mytroops[i] > os_sf * ostroops[i]:
                reploy = Rf * (mytroops[i] - ostroops[i]) / (length - i)
                for j in range(i, len(mytroops)):
                    mytroops[j] += reploy
                os_sf -= Lf
                iwin += 1
            elif my_sf * mytroops[i] < os_sf * ostroops[i]:
                reploy = Rf * (ostroops[i] - mytroops[i]) / (length - i)
                for j in range(i, len(mytroops)):
                    ostroops[j] += reploy
                my_sf -= Lf
                iwin -= 1
        if iwin > 0:
            wins += 2
        elif iwin == 0:
            wins += 1 
    return wins

class Phenotype(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def fitness(self): pass


class OneMaxPhenotype(Phenotype):

    def __init__(self, genotype, generation):
        assert isinstance(genotype, geno.BitVectorGenotype)
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

class BlottoPhenotype(Phenotype):

    def __init__(self, genotype, ea):
        #print genotype, isinstance(genotype, main.BitVectorGenotype)
        #assert isinstance(genotype, BitVectorGenotype)
        self.strategy = []
        self.genotype = genotype
        for i in range(0, len(genotype.vector), 10):
            self.strategy.append(sum(genotype.vector[i:i+10]))
        tmsum = sum(self.strategy,0.0)
        for i in range(len(self.strategy)):
            self.strategy[i] /= tmsum
        self._fitness = None
        self.ea = ea

    @property
    def fitness(self):
        if self._fitness:
            return self._fitness
        else:
            assert 0 <= self.genotype.args['Rf'] <= 1
            assert 0 <= self.genotype.args['Lf'] <= 1
            self._fitness = simulate_war(self, self.ea.pts, self.genotype.args['Rf'], self.genotype.args['Lf'])
            return self._fitness

    @property
    def strategy_entropy(self):
        tsum = 0
        for p in self.strategy:
            if p != 0:
                tsum -= p * math.log(p, 2)
        return tsum

    def __repr__(self):
        s = "<BlottoPhenotype("
        s += ", ".join("%.2f"%x for x in self.strategy)
        s += ")"
        return s
