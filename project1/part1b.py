from main import *
import main


Rf = 0.5
Lf = 0.5

def simulate_war(this, others):
    wins = 0.0
    for os in others:
        iwin = 0
        for t,o in zip(this, os.strategy):
            if t > o:
                iwin += 1
            elif t < o:
                iwin -= 1
        if iwin > 0:
            wins += 1
        elif iwin == 0:
            wins += 0.5
    return wins / len(others)




class BlottoPhenotype(Phenotype):

    def __init__(self, genotype, ea):
        #print genotype, isinstance(genotype, main.BitVectorGenotype)
        #assert isinstance(genotype, BitVectorGenotype)
        self.strategy = []
        self.genotype = genotype
        for i in range(0, len(genotype.vector), 10):
            self.strategy.append(sum(genotype.vector[i:i+10]))
        self._fitness = None
        self.ea = ea

    @property
    def fitness(self):
        if self._fitness:
            return self._fitness
        else:
            self._fitness = simulate_war(self.strategy, self.ea.pts)
            return self._fitness

