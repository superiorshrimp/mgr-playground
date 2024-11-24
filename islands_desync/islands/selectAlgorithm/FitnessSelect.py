import ray
from time import sleep

from .SelectAlgorithm import SelectAlgorithm

from math import inf

class MinFitnessSelect(SelectAlgorithm):
    def __init__(self):
        super().__init__()

    def get_island_relevant_data(self, islands):
        r = [island.get_fitness.remote() for island in islands]
        sleep(0.5)
        return r

    def choose(self, islands, islands_relevant_data, population_member):
        min_val = inf
        min_i = 0
        for i, island in enumerate(islands):
            island_fitness = islands_relevant_data[i]
            if island_fitness < min_val:
                min_val = island_fitness
                min_i = i
        return islands[min_i]
