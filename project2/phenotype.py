from __future__ import division
from abc import ABCMeta, abstractmethod, abstractproperty
import main
import genotype as geno
import math
import itertools
import matplotlib.pyplot as plt

from random import randint, random, shuffle

def read_training_data(number):
    f = open('training_data/izzy-train'+number+'.dat', 'r')
    training_data = [x for x in f.read().split(" ")]
    f.close()
    return training_data

def find_spikes(data, threshold):
    spikes = []
    for point in xrange(len(data)-5):
        max = 0
        for i in range(5):
            if data[point+i] > max:
                max = data[point+i]
        if data[point+2] > threshold and data[point+2] == max:
            spikes.append(point+2)
    return spikes

def d_st(T_a, T_b, p):
    sigma = 0
    for t_ai, t_bi in itertools.izip(T_a, T_b):
        sigma += math.pow(math.fabs(t_ai - t_bi), p)
    return (1/len(min(T_a,T_b,key=len)))*math.pow(sigma, (1/p))

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
        self.a = sum(self.genotype.vector[0:199])/1000
        self.b = sum(self.genotype.vector[200:229])/100
        self.c = -sum(self.genotype.vector[230:280])-30
        self.d = sum(self.genotype.vector[281:380])/10
        self.k = sum(self.genotype.vector[381:480])/100
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
        T_a = find_spikes(self.spike_train, 0)
        T_b = find_spikes(read_training_data('1'), 0)
        return 1/d_st(T_a, T_b, 2)

    def __repr__(self):
        s = "<IzhikevichPhenotype("
        s += ", ".join("%.2f"%x for x in self.spike_train)
        s += ")"
        return s



