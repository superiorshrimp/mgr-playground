import os
from fileinput import filename
from math import inf
import numpy as np
from matplotlib import pyplot as plt
import re

# RESULTS_PATH = 'results/selection/maxfit_0-1/'
RESULTS_PATH = 'results/selection/maxfit/'
# RESULTS_PATH = 'results/selection/minfit/'
# RESULTS_PATH = 'results/selection/stdev/'
# RESULTS_PATH = 'results/selection/sndev/'
# RESULTS_PATH = 'results/selection/random/'

def main():
    y_values = {}
    coef_values = set()

    for filename in os.listdir(RESULTS_PATH):
        if filename.startswith('g-'):
            filename_pattern = re.compile(r"g-c(.+)d(\d+)-\d+")

            match = filename_pattern.search(filename)

            coef_val = match.group(1)
            d_val = int(match.group(2))

            # print(coef_val, d_val)

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

    print(avg_y_values)

    # for d_key in sorted(y_values.keys()):
    #     for coef_key in sorted(coef_values):
    #         print(d_key, coef_key, avg_y_values[d_key])
    #
    # print(avg_y_values)


    colors = ['blue', 'orange', 'green']
    i = 0
    for d_key in sorted(y_values.keys()):
        plt.plot(avg_y_values[d_key], color=colors[i], label='delay = ' + str(d_key), alpha=0.7)
        i += 1

    plt.axhline(0.01278, color=colors[0], linestyle='--')
    plt.axhline(0.01343, color=colors[1], linestyle='--')
    plt.axhline(0.01490, color=colors[2], linestyle='--')

    print(avg_y_values)

    x_vals = list(coef_values)
    plt.xticks(ticks=[_ for _ in range(len(x_vals))], labels=sorted(x_vals))
    plt.ylabel('average best fitness')
    plt.xlabel('selection_method_coef')
    plt.tight_layout()
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
