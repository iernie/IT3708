from __future__ import division
from abc import ABCMeta, abstractmethod, abstractproperty
import main
import genotype as geno
import math
import itertools
import matplotlib.pyplot as plt

from random import randint, random, shuffle
import time

def read_training_data(number):
    f = open('training_data/izzy-train'+number+'.dat', 'r')
    training_data = [float(x) for x in f.read().split(" ") if x]
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


training_data = read_training_data('1')
T_b = find_spikes(training_data, 0)

def d_st(T_a, T_b, p):
    sigma = 0
    for t_ai, t_bi in itertools.izip(T_a, T_b):
        sigma += math.pow(math.fabs(t_ai - t_bi), p)
    nv = math.pow(sigma, (1/p))
    if min(len(T_a),len(T_b)) == 0:
        nv += abs(len(T_a) - len(T_b))*1000
        return nv
    else:
        nv += abs(len(T_a) - len(T_b))*1000/min(len(T_a),len(T_b))
    return (1/min(len(T_a),len(T_b)))*nv

class Phenotype(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def fitness(self): pass


class IzhikevichPhenotype(Phenotype):
    Rv = 0

    def __init__(self, genotype, generation):
        assert isinstance(genotype, geno.BitVectorGenotype)
        #assert len(genotype.vector) == 481
        self.genotype = genotype
        self.generation = generation
        #self.a = sum(self.genotype.vector[0:200])/1000
        #self.b = sum(self.genotype.vector[200:230])/100
        ##self.c = -sum(self.genotype.vector[230:281])-30
        #self.d = sum(self.genotype.vector[281:381])/10
        #self.k = sum(self.genotype.vector[381:481])/100

        A = [1,2,4,16,32,60,84]
        B = [1,2,4,10,13]
        C = [1,2,4,16,19]
        D = [1,2,4,8,16,32,36]
        self.a = (sum([a*x for a,x in zip(A, genotype.vector[0:7])])+1)/1000 
        self.b = (sum([a*x for a,x in zip(B, genotype.vector[7:12])])+1)/100
        self.c = -sum([a*x for a,x in zip(C, genotype.vector[12:17])])-30
        self.d = (sum([a*x for a,x in zip(D,self.genotype.vector[17:24])])+1)/10
        self.k = (sum([a*x for a,x in zip(D,self.genotype.vector[24:31])])+1)/100

        self.tau = 10
        self.I = 10

        self.v = -60
        self.u = 0

        self.spike_threshold = 35
        self.spike_train = []

        for i in range(1001):
            if self.v > self.spike_threshold:
                self.v = self.c
                self.u += self.d
            self.v += (1/self.tau)*(self.k*self.v*self.v + 5*self.v + 140 + self.I - self.u)
            self.u += (self.a/self.tau)*(self.b*self.v - self.u)
            self.spike_train.append(self.v)

        self.T_a = find_spikes(self.spike_train, 0)

    @property
    def fitness2(self):
        #print len(T_a)
        
        #print T_b
        d = (d_st(self.T_a, T_b, 2)+1)
        return 1/d/d

    @property
    def fitness(self):
        #tsum = abs(len(self.T_a)-len(T_b))*1001
        tsum = 0
        p = 2
        for va,vb in zip(self.spike_train, training_data):
            tsum += (va-vb)**p
        tsum = tsum**(1/p)
        tsum /= 1001
        return 1/tsum

    def __repr__(self):
        if self.Rv <= 99:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(self.spike_train)
            ax.plot(training_data)
            fig.savefig("spiketrains/%s.png"%self.Rv)
        IzhikevichPhenotype.Rv += 1

        s = "<IzhikevichPhenotype("
        s += "%s %s %s %s %s %s"%(self.a,
                self.b,
                self.c,
                self.d,
                self.k,
                len(self.T_a))
        #s += ", ".join("%.2f"%x for x in self.spike_train)
        s += ")"
        return s



