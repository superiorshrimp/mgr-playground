from math import inf

import ray
from geneticAlgorithm.run_hpc.run_algorithm_params import (
    RunAlgorithmParams,
)
from islands.core.Computation import Computation
from islands.core.SignalActor import SignalActor
from islands.selectAlgorithm import SelectAlgorithm

@ray.remote(num_cpus=1)
class Island:
    def __init__(self, island_id: int, select_algorithm: SelectAlgorithm):
        self.island_id: int = island_id
        self.computation = None
        self.islands: [Island] = []
        self.immigrants = []
        self.select_algorithm: SelectAlgorithm = select_algorithm
        self.population = []
        self.max_fitness = inf
        self.std_dev = inf

    def start(
        self, island_handle: ray.ObjectRef, islands: ["Island"], algorithm_params: RunAlgorithmParams, signal_actor: SignalActor
    ):
        self.islands = islands
        self.computation = Computation.remote(
            island_handle,
            self.island_id,
            islands,
            self.select_algorithm,
            algorithm_params,
            signal_actor
        )

        return self.computation

    def set_population(self, population):
        self.population = population

    def get_population(self):
        return self.population

    def set_fitness(self, fitness):
        self.max_fitness = fitness

    def get_fitness(self):
        return self.max_fitness

    def set_std_dev(self, std_dev):
        self.std_dev = std_dev

    def get_std_dev(self): # TODO: reorder
        return self.std_dev

    def receive_immigrant(self, immigrant_iteration): # TODO: maybe here
        self.immigrants.append(immigrant_iteration)

    def get_immigrants(self):
        return [self.immigrants.pop(0) for _ in self.immigrants]

    def __repr__(self):
        return "Island %s" % self.island_id
