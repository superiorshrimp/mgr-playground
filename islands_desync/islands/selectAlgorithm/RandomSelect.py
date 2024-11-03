import random

from .SelectAlgorithm import SelectAlgorithm


class RandomSelect(SelectAlgorithm):
    def __init__(self):
        super().__init__()

    def get_island_relevant_data(self, islands):
        pass

    def choose(self, islands, islands_relevant_data, migrant):
        return random.choice(islands)
