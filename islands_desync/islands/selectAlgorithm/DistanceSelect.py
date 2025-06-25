import ray

from .SelectAlgorithm import SelectAlgorithm

class MaxDistanceSelect(SelectAlgorithm):
    def __init__(self):
        super().__init__()

    def get_island_relevant_data(self, islands):
        return [island.get_population.remote() for island in islands]

    def choose(self, islands, islands_relevant_data, migrant):
        max_val = 0
        max_i = 0
        for i, island in enumerate(islands):
            island_population = islands_relevant_data[i] # genes of agents
            for agent in island_population:
                val = sum([(migrant.x[gene] - agent[gene])**2 for gene in range(len(agent))])
                if val > max_val:
                    max_val = val
                    max_i = i
        return islands[max_i]
