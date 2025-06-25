import ray

from .SelectAlgorithm import SelectAlgorithm

from math import inf

class MaxFitnessSelect(SelectAlgorithm):
    def __init__(self):
        super().__init__()

    def get_island_relevant_data(self, islands):
        return [island.get_fitness.remote() for island in islands]

    def choose(self, islands, islands_relevant_data, population_member):
        max_val = 0.0
        max_i = 0
        for i, island in enumerate(islands):
            island_fitness = islands_relevant_data[i]
            if island_fitness > max_val:
                max_val = island_fitness
                max_i = i
        return islands[max_i]

class MinFitnessSelect(SelectAlgorithm):
    def __init__(self):
        super().__init__()

    def get_island_relevant_data(self, islands):
        return [island.get_fitness.remote() for island in islands]

    def choose(self, islands, islands_relevant_data, population_member):
        min_val = inf
        min_i = 0
        for i, island in enumerate(islands):
            island_fitness = islands_relevant_data[i]
            if island_fitness < min_val:
                min_val = island_fitness
                min_i = i
        return islands[min_i]

