from __future__ import division
from abc import ABCMeta, abstractmethod, abstractproperty
import main
import math

from random import randint, random, shuffle

class Genotype(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def develop(self): pass

    @abstractmethod
    def crossover(self,other): pass

    @abstractmethod
    def mutate(self): pass

class BitVectorGenotype(Genotype):

    def __init__(self, vector, length, phenotype, **kwargs):
        if vector == None:
            self.vector = []
            for i in range(length):
                self.vector.append(randint(0,1))
        else:
            self.vector = vector
        self.length = length
        self.phenotype = phenotype
        self.args = kwargs

    def crossover(self, other):
        assert isinstance(other, BitVectorGenotype)
        assert len(self.vector) == len(other.vector)
        i = randint(0,len(self.vector))
        if randint(0,1) == 0:
            return BitVectorGenotype(
                    other.vector[:i] + self.vector[i:],
                    self.length, 
                    self.phenotype, **self.args)
        else:
            return BitVectorGenotype(
                    self.vector[:i] + other.vector[i:],
                    self.length,
                    self.phenotype, **self.args)

    def mutate(self):
        i = randint(0,len(self.vector)-1)
        h = self.vector
        h[i] = (h[i] + 1)&1
        return BitVectorGenotype(h,
                self.length,
                self.phenotype, **self.args)

    def develop(self, i):
        return self.phenotype(self, i)

    def __repr__(self):
        return "<BitVectorGenotype()>"