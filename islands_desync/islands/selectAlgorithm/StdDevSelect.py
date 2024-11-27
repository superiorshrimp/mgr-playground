import ray
# from time import sleep
from asyncio import sleep

from .SelectAlgorithm import SelectAlgorithm

from math import inf

class MinStdDevSelect(SelectAlgorithm):
    def __init__(self):
        super().__init__()

    def get_island_relevant_data(self, islands):
        r = [island.get_std_dev.remote() for island in islands]
        # await sleep(0.5)
        return r

    def choose(self, islands, islands_relevant_data, migrant):
        min_val = inf
        min_i = 0
        for i, island in enumerate(islands):
            island_std_dev = islands_relevant_data[i]
            if island_std_dev < min_val:
                min_val = island_std_dev
                min_i = i
        return islands[min_i]
