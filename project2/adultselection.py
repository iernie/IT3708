from __future__ import division
from abc import ABCMeta, abstractmethod, abstractproperty
import main

from abc import ABCMeta, abstractmethod, abstractproperty
from random import randint, random, shuffle

class AdultSelection(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def select(self, pool): pass

    @abstractmethod
    def retain(self, pool): pass

    @abstractmethod
    def produce(self): pass


class A_I(AdultSelection):
    # Full Generational Replacement
    def __init__(self, population):
        self.population = population

    def select(self, pool):
        return pool

    def retain(self, pool):
        return []

    def produce(self):
        return self.population


class A_II(AdultSelection):
    # Over-production
    def __init__(self, no_adults, no_children):
        self.no_adults = no_adults
        self.no_children = no_children

    def select(self, pool):
        return sorted(pool, key=lambda x: x.fitness, reverse=True)[:self.no_adults]

    def retain(self, pool):
        return []

    def produce(self):
        return self.no_children

class A_III(AdultSelection):
    # Generational Mixing
    def __init__(self, no_adults, no_children):
        self.no_adults = no_adults
        self.no_children = no_children
    
    def select(self, pool):
        return sorted(pool, key=lambda x: x.fitness, reverse=True)[:self.no_adults]
    
    def retain(self, pool):
        return pool
    
    def produce(self):
        return self.no_children
