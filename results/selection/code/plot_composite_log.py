import os
from fileinput import filename
from math import inf
import numpy as np
from matplotlib import pyplot as plt
import re

RESULTS_PATH = 'results/selection/'

def main():
    y_values = {}
    coef_values = set()

    for filename in os.listdir(RESULTS_PATH):
        if filename.startswith('g-'):
            filename_pattern = re.compile(r"g-c(.+)d(\d+)-\d+")

            match = filename_pattern.search(filename)

            coef_val = match.group(1)
            d_val = int(match.group(2))

            print(coef_val, d_val)

            # if coef_val < "0.4":
            #     continue

            coef_values.add(coef_val)

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
                        print("ERROR!", filename)

            if min_fitness_in_file != float(inf):
                if y_values.get(d_val, None) is None:
                    y_values[d_val] = {}
                if y_values[d_val].get(coef_val, None) is None:
                    y_values[d_val][coef_val] = [min_fitness_in_file]
                else:
                    y_values[d_val][coef_val].append(min_fitness_in_file)

    print(y_values)

    avg_y_values = {}
    for d_key in sorted(y_values.keys()):
        avg_y_values[d_key] = []
        for coef_key in sorted(coef_values):
            avg_y_values[d_key].append(np.mean(y_values[d_key][coef_key]))

    for d_key in sorted(y_values.keys()):
        for coef_key in sorted(coef_values):
            print(d_key, coef_key, avg_y_values[d_key])
    print("a")
    print(avg_y_values)

    for d_key in sorted(y_values.keys()):
        plt.plot(avg_y_values[d_key], label='delay = ' + str(d_key), alpha=0.7)

    x_vals = list(coef_values)
    plt.xticks(ticks=[_ for _ in range(len(x_vals))], labels=sorted(x_vals))
    plt.ylabel('average best fitness')
    plt.xlabel('coef')
    plt.tight_layout()
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
