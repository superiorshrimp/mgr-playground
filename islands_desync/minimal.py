import json
from datetime import datetime
from sys import argv

import ray

from geneticAlgorithm.run_hpc.run_algorithm_params import RunAlgorithmParams
from islands.core.IslandRunner import IslandRunner
from islands.selectAlgorithm import RandomSelect, MaxDistanceSelect, MinFitnessSelect, MaxFitnessSelect, MinStdDevSelect
from islands.topologies import CompleteTopology, RingTopology

'''
args:
    1. island count
    2. number of migrants
    3. migration interval
    4. topology
    5. island selection algorithm
    6. blocking
'''
def main():
    now = datetime.now()
    formatted_time = now.strftime('g%H%M%S') + f"{now.microsecond // 1000:03d}"
    params = RunAlgorithmParams(
        island_count=int(argv[1]),
        number_of_emigrants=int(argv[2]),
        migration_interval=int(argv[3]),
        dda=datetime.now().strftime('%y%m%d'),
        tta=formatted_time,
        series_number=1,
        blocking=(argv[6] == "1"),
    )

    topology = get_topology(argv[4])
    select_algorithm = get_island_selection_method(argv[5])

    computation_refs = IslandRunner(
        topology,
        select_algorithm,
        params,
    ).create()

    results = ray.get(computation_refs)

    iterations = {result["island"]: result for result in results}

    with open("logs/iterations_per_second" + datetime.now().strftime("%m-%d-%Y_%H%M") + ".json", "w") as f:
        json.dump(iterations, f)

def get_topology(topology: str):
    match topology:
        case 'CompleteTopology': return CompleteTopology
        case 'RingTopology': return RingTopology
        case _: # TODO: matching reszty topologii
            print("WRONG TOPOLOGY NAME")
            exit()

def get_island_selection_method(method: str):
    match method:
        case 'RandomSelect': return RandomSelect
        case 'MaxDistanceSelect': return MaxDistanceSelect
        case 'MinStdDevSelect': return MinStdDevSelect
        case 'MinFitnessSelect': return MinFitnessSelect
        case 'MaxFitnessSelect': return MaxFitnessSelect
        case _:
            print("WRONG ISLAND SELECTION ALGORITHM NAME")
            exit()

if __name__ == "__main__":
    ray.init(address="127.0.0.1:6379")
    assert ray.is_initialized()

    main()
