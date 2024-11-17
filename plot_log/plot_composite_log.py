import os
from math import inf
import numpy as np
from matplotlib import pyplot as plt

HISTORY_PATH = 'history/'

def main():
    best_fitnesses = []
    fitnesses = []
    result_files = os.listdir(HISTORY_PATH)
    for file in result_files:
        with open(HISTORY_PATH + file, 'r') as f:
            lines = f.readlines()
            best_value = inf
            fitnesses.append([])
            print(lines)
            for line in lines:
                values = float(line.split()[1])
                fitnesses[-1].append(values)
                best_value = min(values, best_value)
            best_fitnesses.append(best_value)

    plt.plot([_ for _ in range(len(result_files))], best_fitnesses)
    plt.axhline(np.mean(best_fitnesses), color='red', label='mean', linestyle='--', )
    plt.y_label = 'best fitness'
    plt.x_label = 'computation'
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
