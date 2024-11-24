import ray
from time import sleep

from .SelectAlgorithm import SelectAlgorithm

class MaxDistanceSelect(SelectAlgorithm):
    def __init__(self):
        super().__init__()

    def get_island_relevant_data(self, islands):
        r = [island.get_population.remote() for island in islands]
        sleep(0.5)
        return r

    def choose(self, islands, islands_relevant_data, migrant):
        max_val = 0
        max_i = 0
        for i, island in enumerate(islands):
            island_population = islands_relevant_data[i]
            for agent in island_population:
                val = sum([(migrant[0].x[gene] - agent.x[gene])**2 for gene in range(len(agent.x))])
                if val > max_val:
                    max_val = val
                    max_i = i
        return islands[max_i]
