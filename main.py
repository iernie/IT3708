from abc import ABCMeta, abstractmethod
from random import randint

class EA(object):
    def __init__(self):
        self.population = []

class Genotype(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def develop(self): pass

class BitVectorGenotype(Genotype):

    def __init__(self, length=10, vector=None):
        if vector == None:
            self.vector = []
            for i in range(length):
                self.vector.append(randint(0,1))
        else:
            self.vector = vector

    

class Phenotype(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def fitness(self): pass

class AdultSelection(object):
    __metaclass__ = ABCMeta

class A_I(AdultSelection):
    # Full Generational Replacement
    pass

class A_II(AdultSelection):
    # Over-production
    pass

class A_III(AdultSelection):
    # Generational Mixing
    pass


class ParentSelection(object):
    __metaclass__ = ABCMeta

if __name__ == '__main__':
    pass
