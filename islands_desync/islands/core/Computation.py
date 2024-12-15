from typing import List
import json
import pika
import ray

from geneticAlgorithm.migrations.ray_migration_pipeline import RayMigrationPipeline
from geneticAlgorithm.migrations.queue_migration import QueueMigration
from geneticAlgorithm.run_hpc.create_algorithm_hpc import emas_create_algorithm_hpc
from geneticAlgorithm.run_hpc.run_algorithm_params import RunAlgorithmParams
from islands.core.Emigration import Emigration
from islands.core.SignalActor import SignalActor


@ray.remote(num_cpus=1)
class Computation:
    def __init__(
        self,
        island: ray.ObjectRef,
        island_id: int,
        islands: List[ray.ObjectRef],
        select_algorithm,
        algorithm_params: RunAlgorithmParams,
        signal_actor: SignalActor
    ):
        self.island = island
        self.island_id = island_id
        self.emigration = Emigration(islands, select_algorithm)
        self.migration = RayMigrationPipeline(island, self.emigration, signal_actor) # TODO: delay refactor
        self.algorithm = emas_create_algorithm_hpc(self.island, island_id, self.migration, algorithm_params)

    def start(self):
        print("Starting computation")
        self.algorithm.run()
        result = self.algorithm.get_result()

        calculations = {
            "island": self.island_id,
            "iterations": self.algorithm.step_num,
            # "time": self.migration.run_time(),
            # "ips": self.algorithm.step_num / self.migration.run_time(),
            # "start": self.migration.start,
            # "end": self.migration.end,
        }

        print(f"\nIsland: {self.island_id} Fitness: {result.fitness}")

        return calculations
