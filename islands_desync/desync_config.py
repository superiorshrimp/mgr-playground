import json
import os
from sys import argv

PATH = './islands_desync/geneticAlgorithm/algorithm/configurations/algorithm_configuration.json'

def complete(delay, n):
    T = [
        [delay if i != j else -1 for i in range(n)] for j in range(n)
    ]

    return T

def ring(delay, n):
    T = [
        [delay if abs(i-j) == 1 else -1 for i in range(n)] for j in range(n)
    ]

    T[0][-1] = delay
    T[-1][0] = delay

    return T

def print_array(T):
    for i in range(len(T)):
        for j in range(len(T[i])):
            print(T[i][j], end=" ")
        print()

def save(T, select_algo_coef):
    with open(PATH, 'r') as f:
        data = json.load(f)
        data['island_delays'] = {
            str(i): T[i] for i in range(len(T))
        }
        if select_algo_coef is not None:
            data['select_algo_coef'] = select_algo_coef
    print(data)

    os.remove(PATH)

    with open(PATH, 'w+') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    n = int(argv[1])
    delay = int(argv[2])
    topology = argv[3]
    select_algo_coef = None
    if argv[4]:
        select_algo_coef = float(argv[4])

    T = None
    if topology == "ring":
        T = ring(delay, n)
    elif topology == "complete":
        T = complete(delay, n)
    else:
        print("topology must be either 'ring' or 'complete'; chosen:", topology)
        exit(1)
    print_array(T)
    save(T, select_algo_coef)

