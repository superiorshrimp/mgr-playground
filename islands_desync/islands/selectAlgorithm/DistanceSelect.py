import ray

from .SelectAlgorithm import SelectAlgorithm

class MaxDistanceSelect(SelectAlgorithm):
    def __init__(self):
        super().__init__()

    def choose(self, items, migrant):
        max_val = 0
        max_i = 0
        for i, island in enumerate(items):
            island_population = ray.get(island.get_population.remote())
            for agent in island_population:
                val = sum([(migrant[0].x[gene] - agent.x[gene])**2 for gene in range(len(agent.x))])
                if val > max_val:
                    max_val = val
                    max_i = i
        return items[max_i]
