from datetime import datetime
import ray
import json

from geneticAlgorithm.run_hpc.run_algorithm_params import RunAlgorithmParams
from islands.topologies.CompleteTopology import CompleteTopology
from islands.core.IslandRunner import IslandRunner
from islands.selectAlgorithm import RandomSelect


def main():
    params = RunAlgorithmParams(
        island_count=3,
        number_of_emigrants=5,
        migration_interval=5,
        dda=datetime.now().strftime('%y%m%d'),
        tta=datetime.now().strftime('g%H%M%S'),
        series_number=1,
    )

    computation_refs = IslandRunner(
        CompleteTopology,
        RandomSelect,
        params,
    ).create()

    results = ray.get(computation_refs)

    iterations = {result["island"]: result for result in results}

    with open(
        "logs/"
        + "iterations_per_second"
        + datetime.now().strftime("%m-%d-%Y_%H%M")
        + ".json",
        "w",
    ) as f:
        json.dump(iterations, f)

if __name__ == "__main__":
    ray.init(address="127.0.0.1:6379")
    assert ray.is_initialized()

    main()