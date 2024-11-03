from datetime import datetime
from matplotlib import pyplot as plt
import ray
import os
import numpy as np
import json
from sys import argv

from geneticAlgorithm.run_hpc.run_algorithm_params import RunAlgorithmParams
from islands.topologies.CompleteTopology import CompleteTopology
from islands.core.IslandRunner import IslandRunner
from islands.selectAlgorithm import DistanceSelect, RandomSelect, MaxDistanceSelect, MinFitnessSelect, MinStdDevSelect

# TODO
def main():
    dda = datetime.now().strftime('%y%m%d')
    tta = datetime.now().strftime('g%H%M%S')
    params = RunAlgorithmParams(
        island_count=int(argv[1]),
        number_of_emigrants=int(argv[2]),
        migration_interval=int(argv[3]),
        dda=dda,
        tta=tta,
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
            plot_history(dda, tta)

    # iterations = {result["island"]: result for result in results}
    # with open(
    #     "logs/"
    #     + "iterations_per_second"
    #     + datetime.now().strftime("%m-%d-%Y_%H%M")
    #     + ".json",
    #     "w",
    # ) as f:
    #     json.dump(iterations, f)

def plot_history(dda, tta):
    variances = {}
    fitnesses = {}
    alive_counts = {}

    max_iter = 0
    for filename in os.scandir("history/" + dda + "/" + tta):
        if filename.is_file():
            with open(filename, "r") as f:
                island = int(filename.name.split("/")[-1].split(".")[0])
                obj = json.load(f)
                variances[island] = obj["variance"]
                fitnesses[island] = obj["fitness"]
                alive_counts[island] = obj["alive"]
                max_iter = max(max_iter, len(variances[island]))

    iter = [i for i in range(max_iter)]
    pad(max_iter, [variances, fitnesses, alive_counts])
    avg_windows_size = 100
    for island in variances.keys():
        plt.plot(iter, variances[island])
        # plt.plot(iter[avg_windows_size:], [np.mean(variances[island][i:i+avg_windows_size]) for i in range(len(iter)-avg_windows_size)])
    plt.xticks(iter[avg_windows_size::100], rotation=45)
    plt.ylim([0, 2])
    plt.xlabel('iteration')
    plt.savefig('dev.png')
    plt.clf()

    for island in variances.keys():
        plt.plot(iter, fitnesses[island])
    plt.xticks(iter[::100], rotation=45)
    plt.ylim([0, 100])
    plt.xlabel('iteration')
    plt.savefig('fit.png')
    plt.clf()

    for island in variances.keys():
        plt.plot(iter, alive_counts[island])
    plt.xlabel('iteration')
    plt.xticks(rotation=45)
    plt.savefig('liv.png')

def pad(max_iter, list_of_lists):
    for lists in list_of_lists:
        for key, l in lists.items():
            l += [None] * (max_iter - len(l))

if __name__ == "__main__":
    ray.init(address="127.0.0.1:6379")
    assert ray.is_initialized()

    main()