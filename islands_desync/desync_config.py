import json
import os

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

def save(T):
    with open(PATH, 'r') as f:
        data = json.load(f)
        data['island_delays'] = {
            str(i): T[i] for i in range(len(T))
        }
    print(data)

    os.remove(PATH)

    with open(PATH, 'w+') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    delay = 10
    n = 3
    T = ring(delay, n)
    print_array(T)
    save(T)

