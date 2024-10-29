import ray

from .SelectAlgorithm import SelectAlgorithm

from math import inf

class MinFitnessSelect(SelectAlgorithm):
    def __init__(self):
        super().__init__()

    def choose(self, items, migrant):
        min_val = inf
        min_i = 0
        for i, island in enumerate(items):
            island_fitness = ray.get(island.get_fitness.remote())
            if island_fitness < min_val:
                min_val = island_fitness
                min_i = i
        return items[min_i]
