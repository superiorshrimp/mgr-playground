from typing import Dict, List

import ray

from islands.core.Emigration import Emigration
from islands.core.Migration import Migration
from islands.core.SignalActor import SignalActor


class RayMigration(Migration):
    def __init__(self, islandActor, emigration: Emigration, signal_actor: SignalActor):
        super().__init__()
        self.emigration = emigration
        self.islandActor = islandActor
        self.signal_actor: SignalActor = signal_actor

    def migrate_individuals(
        self, individuals_to_migrate, iteration_number, island_number, ind_timestamp
    ):
        # print("Emigracja %s iter: %s" % (island_number, iteration_number))
        for individual in individuals_to_migrate:
            # print("%s: Emigruje %s" % (self.islandActor, individual))
            self.emigration.emigrate.remote((individual, iteration_number, ind_timestamp))

    def receive_individuals(
        self, step_num: int, evaluations: int
    ) :
        new_individuals = ray.get(self.islandActor.get_immigrants.remote())

        new_individuals, migrant_iteration_numbers, ind_timestamp = zip(*new_individuals)

        migration_at_step_num = {
            "step": step_num,
            "ev": evaluations,
            "iteration_numbers": migrant_iteration_numbers,
            "timestamps": ind_timestmp,
        }

        return list(new_individuals), migration_at_step_num

    def wait_for_all_start(self):
        self.signal_actor.send.remote()
        ray.get(self.signal_actor.wait.remote())

    def wait_for_finish(self):
        ray.get(self.signal_actor.wait.remote("finish"))

    def signal_finish(self):
        self.signal_actor.send.remote("finish")
