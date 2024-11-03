from abc import ABC, abstractmethod


class SelectAlgorithm(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_island_relevant_data(self, islands):
        pass

    @abstractmethod
    def choose(self, islands, islands_relevant_data, migrant):
        pass
