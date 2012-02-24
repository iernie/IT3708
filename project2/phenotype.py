from __future__ import division
from abc import ABCMeta, abstractmethod, abstractproperty
import main
import genotype as geno
import math

from random import randint, random, shuffle

def number_of_ones(array):
    ones = 0
    for i in [x for x in array if x == 1]:
        ones += ones
    return ones

class Phenotype(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def fitness(self): pass


class IzhikevichPhenotype(Phenotype):

    def __init__(self, genotype, generation):
        assert isinstance(genotype, geno.BitVectorGenotype)
        assert len(genotype.vector) == 481
        self.genotype = genotype
        self.generation = generation
        self.a = number_of_ones(self.genotype.vector[0:199])/1000
        self.b = number_of_ones(self.genotype.vector[200:229])/100
        self.c = -number_of_ones(self.genotype.vector[230:280])-30
        self.d = number_of_ones(self.genotype.vector[281:380])/10
        self.k = number_of_ones(self.genotype.vector[381:480])/100
        self.tau = 10
        self.I = 10

        self.v = -60
        self.u = 0

        self.spike_threshold = 35
        self.spike_train = []

        for i in range(1000):
            if self.v > self.spike_threshold:
                self.v = self.c
                self.u += self.d
            self.v += (1/self.tau)*(self.k*self.v*self.v + 5*self.v + 140 + self.I)
            self.u += (self.a/self.tau)*(self.b*self.v - self.u)
            self.spike_train.append(self.v)

    @property
    def fitness(self):
        pass

    def __repr__(self):
        s = "<IzhikevichPhenotype("
        s += ", ".join("%.2f"%x for x in self.spike_train)
        s += ")"
        return s



