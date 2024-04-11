from typing import Dict, List

import ray

from geneticAlgorithm.migrations.ray_migration import RayMigration
from islands.core.Emigration import Emigration
from islands.core.SignalActor import SignalActor


class RayMigrationPipeline(RayMigration):
    def __init__(self, islandActor, emigration: Emigration, signal_actor: SignalActor):
        super().__init__(islandActor, emigration, signal_actor)
        self.new_individuals_refs = self.islandActor.get_immigrants.remote()

    def receive_individuals(
        self, step_num: int, evaluations: int
    ) :
        new_individuals = ray.get(self.new_individuals_refs)
        self.new_individuals_refs = self.islandActor.get_immigrants.remote()

        new_individuals, migrant_iteration_numbers, ind_timestamps = zip(*new_individuals)

        migration_at_step_num = {
            "step": step_num,
            "ev": evaluations,
            "iteration_numbers": migrant_iteration_numbers,
            "timestamps": ind_timestamps,
        }

        return list(new_individuals), migration_at_step_num
