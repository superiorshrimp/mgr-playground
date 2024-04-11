import json
import sys
from datetime import datetime
import os
import ray
from islands.core.IslandRunner import IslandRunner
from islands.selectAlgorithm import RandomSelect
from islands.topologies import RingTopology

from geneticAlgorithm.run_hpc.run_algorithm_params import (
    RunAlgorithmParams,
)
from islands.topologies.TorusTopology import TorusTopology
from islands.topologies.CompleteTopology import CompleteTopology

os.environ["RAY_DEDUP_LOGS"] = "0"

def main():
    pass
    # if sys.argv[2] != " ":
    #     ray.init(_temp_dir=sys.argv[2])

    # params = RunAlgorithmParams(
    #     island_count=int(sys.argv[1]),
    #     number_of_emigrants=int(sys.argv[3]),
    #     migration_interval=int(sys.argv[4]),
    #     dda=sys.argv[5],
    #     tta=sys.argv[6],
    #     series_number=1,
    # )

    # computation_refs = IslandRunner(TorusTopology, RandomSelect, params).create()
    # #computation_refs = IslandRunner(RingTopology, RandomSelect, params).create()
    # #computation_refs = IslandRunner(CompleteTopology, RandomSelect, params).create()

    # results = ray.get(computation_refs)

    # iterations = {result["island"]: result for result in results}

    # with open(
    #     "logs/"
    #     + "iterations_per_second"
    #     + datetime.now().strftime("%m-%d-%Y_%H%M")
    #     + ".json",
    #     "w",
    # ) as f:
    #     json.dump(iterations, f)


if __name__ == "__main__":
    main()
