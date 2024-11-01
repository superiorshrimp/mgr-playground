import ray

from .SelectAlgorithm import SelectAlgorithm

from math import inf

class MinStdDevSelect(SelectAlgorithm):
    def __init__(self):
        super().__init__()

    def choose(self, items, migrant):
        min_val = inf
        min_i = 0
        for i, island in enumerate(items):
            island_std_dev = ray.get(island.get_std_dev.remote())
            if island_std_dev < min_val:
                min_val = island_std_dev
                min_i = i
        return items[min_i]
