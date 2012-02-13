from main import *

class BlottoPhenotype(Phenotype):

    def __init__(self, genotype, generation):
        assert isinstance(genotype, BitVectorGenotype)
        self.generation = generation
        self.strategy = []
        for i in range(0, len(genotype.vector), 10):
            self.strategy.append(sum(genotype.vector[i:i+10]))
        print self.strategy


