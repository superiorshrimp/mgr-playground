import ray

from islands.selectAlgorithm import SelectAlgorithm
from islands.selectAlgorithm import RandomSelect


class Emigration:
    def __init__(self, islands, select_algorithm: SelectAlgorithm):
        self.islands = islands
        self.select_algorithm: SelectAlgorithm = select_algorithm

    def emigrate(self, population_member, islands_relevant_data):
        destination = self.select_algorithm.choose(self.islands, islands_relevant_data, population_member)
        destination.receive_immigrant.remote(population_member)
