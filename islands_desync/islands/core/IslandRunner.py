import time
from typing import List

import ray

from random import uniform

from geneticAlgorithm.run_hpc.run_algorithm_params import RunAlgorithmParams
from islands.core.Island import Island
from islands.core.SignalActor import SignalActor
from islands.topologies.TorusTopology import TorusTopology


class IslandRunner:
    def __init__(self, create_topology, select_algorithm, params: RunAlgorithmParams):
        self.CreateTopology = create_topology
        self.SelectAlgorithm = select_algorithm
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

        # return self.start_sync(islands, topology, signal_actor)
        # return self.start_first_desync(islands, topology, signal_actor)
        return self.start_uniform_desync(islands, topology, signal_actor)

    def start_sync(self, islands, topology, signal_actor):
        computations = ray.get([
            island.start.remote(island, topology[island_id], self.params, signal_actor)
            for island_id, island in enumerate(islands)
        ])
        comp_refs = [computation.start.remote() for computation in computations]
        return comp_refs

    def start_first_desync(self, islands, topology, signal_actor):
        first_computation = ray.get(islands[0].start.remote(islands[0], topology[0], self.params, signal_actor))
        first_comp_ref = first_computation.start.remote()

        time.sleep(5)

        computations = ray.get([
            island.start.remote(island, topology[island_id], self.params, signal_actor)
            for island_id, island in enumerate(islands[1:])
        ])

        comp_refs = [first_comp_ref] + [computation.start.remote() for computation in computations]
        return comp_refs

    def start_uniform_desync(self, islands, topology, signal_actor):
        max_late_start = 10
        start_times = [uniform(0,max_late_start) for _ in range(len(islands))]
        start_times.sort()
        comp_refs = []
        computations = ray.get([
            island.start.remote(island, topology[island_id], self.params, signal_actor)
            for island_id, island in enumerate(islands)
        ])

        start_time = time.time()
        i = 0
        while i < len(islands):
            if time.time() - start_time >= start_times[i]:
                comp_refs.append(computations[i].start.remote())
                i += 1

        return comp_refs
