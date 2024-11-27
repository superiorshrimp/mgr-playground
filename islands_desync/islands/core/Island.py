from math import inf

from asyncio import sleep
import ray
from geneticAlgorithm.run_hpc.run_algorithm_params import (
    RunAlgorithmParams,
)
from islands.core.Computation import Computation
from islands.core.SignalActor import SignalActor
from islands.selectAlgorithm import SelectAlgorithm

# SLEEP = 0.1

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

    # async def get_population(self):
    def get_population(self):
        # await sleep(SLEEP)
        return self.population

    def set_fitness(self, fitness):
        self.max_fitness = fitness

    # async def get_fitness(self):
    def get_fitness(self):
        # await sleep(SLEEP)
        return self.max_fitness

    def set_std_dev(self, std_dev):
        self.std_dev = std_dev

    # async def get_std_dev(self): # TODO: reorder
    def get_std_dev(self): # TODO: reorder
        # await sleep(SLEEP)
        return self.std_dev

    def receive_immigrant(self, immigrant_iteration): # TODO: maybe here
        self.immigrants.append(immigrant_iteration)

    # async def get_immigrants(self):
    def get_immigrants(self):
        # await sleep(SLEEP)
        return [self.immigrants.pop(0) for _ in self.immigrants]

    def __repr__(self):
        return "Island %s" % self.island_id
