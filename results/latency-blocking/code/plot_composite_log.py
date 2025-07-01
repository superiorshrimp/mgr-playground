import os
from fileinput import filename
from math import inf
import numpy as np
from matplotlib import pyplot as plt
import re

RESULTS_PATH = 'results/latency-blocking/'

def main():
    y_values_b0 = {}
    y_values_b1 = {}
    d_values = set()

    for filename in os.listdir(RESULTS_PATH):
        if filename.startswith('g-'):
            filename_pattern = re.compile(r"g-b(\d+)d(\d+)-\d+")

            match = filename_pattern.search(filename)

            b_val = int(match.group(1))
            d_val = int(match.group(2))

            d_values.add(d_val)

            min_fitness_in_file = float(inf)
            file_path = RESULTS_PATH + filename

            with open(file_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        fitness = float(line)
                        min_fitness_in_file = min(min_fitness_in_file, fitness)
                    except (ValueError, IndexError):
                        continue

            if min_fitness_in_file != float(inf):
                if b_val == 0:
                    if y_values_b0.get(d_val, None) is None:
                        y_values_b0[d_val] = [min_fitness_in_file]
                    else:
                        y_values_b0.get(d_val).append(min_fitness_in_file)
                else:
                    if y_values_b1.get(d_val, None) is None:
                        y_values_b1[d_val] = [min_fitness_in_file]
                    else:
                        y_values_b1.get(d_val).append(min_fitness_in_file)

    print([y_values_b0[key] for key in sorted(y_values_b0.keys())])
    print([y_values_b1[key] for key in sorted(y_values_b1.keys())])

    avg_y_values_b0 = []
    avg_y_values_b1 = []
    for key in sorted(d_values):
        avg_y_values_b0.append(np.mean(y_values_b0[key]))
        avg_y_values_b1.append(np.mean(y_values_b1[key]))
        print(key, y_values_b0[key], np.mean(y_values_b0[key]))

    print(avg_y_values_b0)
    print(avg_y_values_b1)

    plt.plot(avg_y_values_b0, label='non-blocking', alpha=0.7)
    plt.plot(avg_y_values_b1, label='blocking', alpha=0.7)

    x_vals = list(d_values)
    plt.xticks(ticks=[_ for _ in range(len(x_vals))], labels=sorted(x_vals))
    plt.ylabel('average best fitness')
    plt.xlabel('delay [ms]')
    plt.tight_layout()
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
