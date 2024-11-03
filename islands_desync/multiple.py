from datetime import datetime
import ray
import json
from sys import argv

from geneticAlgorithm.run_hpc.run_algorithm_params import RunAlgorithmParams
from islands.topologies.CompleteTopology import CompleteTopology
from islands.core.IslandRunner import IslandRunner
from islands.selectAlgorithm import DistanceSelect, RandomSelect, MaxDistanceSelect, MinFitnessSelect, MinStdDevSelect


def main():
    params = RunAlgorithmParams(
        island_count=int(argv[1]),
        number_of_emigrants=int(argv[2]),
        migration_interval=int(argv[3]),
        dda=datetime.now().strftime('%y%m%d'),
        tta=datetime.now().strftime('g%H%M%S'),
        series_number=1,
    )

    n_tries = 10

    island_select_algorithms = [
        RandomSelect,
        MaxDistanceSelect,
        MinStdDevSelect,
        MinFitnessSelect,
    ]

    for algo in island_select_algorithms:
        for i in range(n_tries):
            computation_refs = IslandRunner(
                CompleteTopology,
                algo,
                params,
            ).create()

            results = ray.get(computation_refs)

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
    ray.init(address="127.0.0.1:6379")
    assert ray.is_initialized()

    main()