import time
from typing import List

import ray

from geneticAlgorithm.run_hpc.run_algorithm_params import RunAlgorithmParams
from islands.core.Island import Island
from islands.core.SignalActor import SignalActor
from islands.topologies.TorusTopology import TorusTopology


class IslandRunner:
    def __init__(self, CreateTopology, SelectAlgorithm, params: RunAlgorithmParams):
        self.CreateTopology = CreateTopology
        self.SelectAlgorithm = SelectAlgorithm
        self.params: RunAlgorithmParams = params

    def create(self) -> List[ray.ObjectRef]:
        islands = [
            Island.remote(i, self.SelectAlgorithm())
            for i in range(self.params.island_count)
        ]

        topology = self.CreateTopology(
            self.params.island_count, lambda i: islands[i]
        )

        if isinstance(topology, TorusTopology):
            topology = topology.create(5, self.params.island_count // 5)
        else:
            topology = topology.create()

        signal_actor = SignalActor.remote(self.params.island_count)

        computations = [
            ray.get(
                islands[0].start.remote(islands[0], topology[0], self.params, signal_actor)
            )
        ]

        time.sleep(15)

        computations.extend(
            ray.get(
                [
                    island.start.remote(island, topology[island_id], self.params, signal_actor)
                    for island_id, island in enumerate(islands[1:])
                ]
            )
        )

        return [computation.start.remote() for computation in computations]
