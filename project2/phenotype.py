from __future__ import division
from abc import ABCMeta, abstractmethod, abstractproperty
import main
import genotype as geno
import math
import matplotlib.pyplot as plt

from random import randint, random, shuffle
import time

SDM = 1
NUM = 1

def read_training_data(number):
    f = open('training_data/izzy-train'+str(number)+'.dat', 'r')
    training_data = [float(x) for x in f.read().strip().split(" ") if x]
    assert len(training_data) == 1001
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


training_data = read_training_data(NUM)
T_b = find_spikes(training_data, 0)

def d_st(T_a, T_b, p):
    sigma = 0
    for t_ai, t_bi in zip(T_a, T_b):
        sigma += abs(t_ai - t_bi)**p
    nv = sigma**(1/p)
    if min(len(T_a),len(T_b)) == 0:
        nv += abs(len(T_a) - len(T_b))*1000
        return nv
    else:
        nv += abs(len(T_a) - len(T_b))*1000/min(len(T_a),len(T_b))
    return (1/min(len(T_a),len(T_b)))*nv

def d_wf(st, td, p):
    #tsum = abs(len(self.T_a)-len(T_b))*1001
    tsum = 0
    for va,vb in zip(st, td):
        tsum += (va-vb)**p
    tsum = tsum**(1/p)
    tsum /= 1001
    return 1/tsum

def d_si(T_a, T_b, p):
    tsum = 0
    N = min(len(T_a), len(T_b))
    for ai, ap, bi, bp in zip(T_a[1:],
            T_a,
            T_b[:1],
            T_b):
        tsum += abs((ai-ap) - (bi-bp))**p
    tsum = tsum ** (1/p)
    if N > 1:
        tsum += abs(len(self.T_a) - len(T_b))*1000/min(len(self.T_a),len(T_b))
        tsum = tsum / (N-1)
    else:
        tsum += abs(len(self.T_a) - len(T_b))*1000
    return (1 / (tsum)) 

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

        A = [1,2,4,8,16,32,60,77]
        B = [1,2,4,8,15]
        C = [1,2,4,8,16,19]
        D = [1,2,4,8,16,32,36]
        self.a = (sum([a*x for a,x in zip(A, genotype.vector[0:8])])+1)/1000 
        self.b = (sum([a*x for a,x in zip(B, genotype.vector[8:13])])+1)/100
        self.c = -sum([a*x for a,x in zip(C, genotype.vector[13:19])])-30
        self.d = (sum([a*x for a,x in zip(D,self.genotype.vector[19:26])])+1)/10
        self.k = (sum([a*x for a,x in zip(D,self.genotype.vector[26:33])])+1)/100

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
    def fitness(self):
        if SDM == 1: # Spike Time
            d = (d_st(self.T_a, T_b, 2)+1)
            return 1/d/d
        elif SDM == 2: # Spike Interval
            return d_si(self.T_a, T_b, 4)
        elif SDM == 3: # Waveform
            return d_wf(self.spike_train, training_data, 2)

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



