import ray

from .SelectAlgorithm import SelectAlgorithm

from math import inf

class MinFitnessSelect(SelectAlgorithm):
    def __init__(self):
        super().__init__()

    def choose(self, islands, islands_relevant_data, population_member):
        min_val = inf
        min_i = 0
        for i, island in enumerate(islands):
            island_fitness = islands_relevant_data[i]
            if island_fitness < min_val:
                min_val = island_fitness
                min_i = i
        return islands[min_i]
