import os
from math import inf
import numpy as np
from matplotlib import pyplot as plt

HISTORY_PATH = 'history/'

def main():
    best_fitnesses = []
    fitnesses = []
    result_files = os.listdir(HISTORY_PATH)
    result_files = list(filter(lambda f: f.startswith('g'), result_files))
    result_files.sort(key=lambda x: int(x.split('-')[1]))
    for file in result_files:
        if file.startswith('g'):
            with open(HISTORY_PATH + file, 'r') as f:
                print(file)
                lines = f.readlines()
                best_value = inf
                fitnesses.append([])
                for line in lines:
                    # print(line, file)
                    if len(line.split()) > 1:
                        values = float(line.split()[1])
                        fitnesses[-1].append(values)
                        best_value = min(values, best_value)
                best_fitnesses.append(best_value)

    print(best_fitnesses)
    plt.plot([1] + [5*(i+1) for i in range(len(best_fitnesses)-1)], best_fitnesses)
    plt.xticks([1] + [5*(i+1) for i in range(len(best_fitnesses)-1)])
    mean = np.mean(best_fitnesses)
    print("mean:", mean)
    print("worst:", max(best_fitnesses))
    print("best:", min(best_fitnesses))
    # plt.axhline(mean, color='red', label='mean', linestyle='--', )
    plt.ylabel('average fitness')
    plt.xlabel('islands')
    # plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
