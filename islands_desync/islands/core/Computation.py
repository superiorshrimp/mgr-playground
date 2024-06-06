import ray

from geneticAlgorithm.migrations.ray_migration_pipeline import (
    RayMigrationPipeline,
)
from geneticAlgorithm.run_hpc.create_algorithm_hpc import (
    create_algorithm_hpc,
    emas_create_algorithm_hpc
)
from geneticAlgorithm.run_hpc.run_algorithm_params import (
    RunAlgorithmParams,
)
from islands.core.Emigration import Emigration
from islands.core.SignalActor import SignalActor


@ray.remote(num_cpus=1)
class Computation:
    def __init__(
        self,
        island,
        n: int,
        islands,
        select_algorithm,
        algorithm_params: RunAlgorithmParams,
        signal_actor: SignalActor
    ):
        print("here")
        self.island = island
        self.n: int = n

        self.emigration = Emigration(islands, select_algorithm)
        self.migration = RayMigrationPipeline(island, self.emigration, signal_actor)

        self.algorithm = emas_create_algorithm_hpc(n, self.migration, algorithm_params)

    def start(self):
        print("Starting comp")
        self.algorithm.run()
        result = self.algorithm.get_result()

        calculations = {
            "island": self.n,
            "iterations": self.algorithm.step_num,
            "time": self.migration.run_time(),
            "ips": self.algorithm.step_num / self.migration.run_time(),
            "start": self.migration.start,
            "end": self.migration.end,
        }

        print(f"\nIsland: {self.n} Fitness: {result.fitness}") #objectives[0]

        return calculations
