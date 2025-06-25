# import os
# from fileinput import filename
# from math import inf
# import numpy as np
# from matplotlib import pyplot as plt
# import re
#
# RESULTS_PATH = 'results/latency-blocking/'
#
# def main():
#     y_values_b0 = {}
#     y_values_b1 = {}
#     d_values = set()
#
#     for filename in os.listdir(RESULTS_PATH):
#         if filename.startswith('g-'):
#             filename_pattern = re.compile(r"g-b(\d+)d(\d+)-\d+")
#
#             match = filename_pattern.search(filename)
#             if not match:
#                 continue
#
#             b_val = int(match.group(1))
#             d_val = int(match.group(2))
#
#             d_values.add(d_val)
#
#             min_fitness_in_file = float(inf)
#             file_path = RESULTS_PATH + filename
#
#             with open(file_path, 'r') as f:
#                 for line in f:
#                     if not line.strip():
#                         continue
#
#                     try:
#                         fitness = float(line)
#                         min_fitness_in_file = min(min_fitness_in_file, fitness)
#                     except (ValueError, IndexError):
#                         continue
#
#             if min_fitness_in_file != float(inf):
#                 if b_val == 0:
#                     y_values_b0.setdefault(d_val, []).append(min_fitness_in_file)
#                 else:
#                     y_values_b1.setdefault(d_val, []).append(min_fitness_in_file)
#
#     x_b0 = []
#     y_b0 = []
#     for d, values in y_values_b0.items():
#         x_b0.extend([d] * len(values))
#         y_b0.extend(values)
#
#     x_b1 = []
#     y_b1 = []
#     for d, values in y_values_b1.items():
#         x_b1.extend([d] * len(values))
#         y_b1.extend(values)
#
#     plt.scatter(x_b0, y_b0, label='b=0', alpha=0.7)
#     plt.scatter(x_b1, y_b1, label='b=1', alpha=0.7)
#
#     plt.ylabel('best fitness')
#     plt.xlabel('delay [ms]')
#     plt.legend()
#     plt.tight_layout()
#     plt.show()
#
#
# if __name__ == "__main__":
#     main()

import os
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
            if not match:
                continue

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
                    y_values_b0.setdefault(d_val, []).append(min_fitness_in_file)
                else:
                    y_values_b1.setdefault(d_val, []).append(min_fitness_in_file)

    def flatten_and_sort(data_dict):
        x = []
        y = []
        for d in sorted(data_dict.keys()):
            values = data_dict[d]
            x.extend([d] * len(values))
            y.extend(values)
        return np.array(x), np.array(y)

    x_b0, y_b0 = flatten_and_sort(y_values_b0)
    x_b1, y_b1 = flatten_and_sort(y_values_b1)

    # Scatter plots
    plt.scatter(x_b0, y_b0, label='b=0', alpha=0.7)
    plt.scatter(x_b1, y_b1, label='b=1', alpha=0.7)

    # Trend lines
    for x, y, color, label in [(x_b0, y_b0, 'blue', 'b=0'), (x_b1, y_b1, 'orange', 'b=1')]:
        coeffs = np.polyfit(x, y, deg=1)
        trend = np.poly1d(coeffs)
        x_sorted = np.linspace(min(x), max(x), 200)
        plt.plot(x_sorted, trend(x_sorted), color=color, linestyle='--', label=f'{label} trend')

    # Optional: show standard deviation bands (can be noisy if many x values repeat)
    def plot_std_band(x_vals, y_dict, color):
        means = []
        stds = []
        x_unique = sorted(y_dict.keys())
        for d in x_unique:
            vals = y_dict[d]
            means.append(np.mean(vals))
            stds.append(np.std(vals))
        means = np.array(means)
        stds = np.array(stds)
        x_unique = np.array(x_unique)
        plt.fill_between(x_unique, means - stds, means + stds, color=color, alpha=0.2)

    plot_std_band(x_b0, y_values_b0, 'blue')
    plot_std_band(x_b1, y_values_b1, 'orange')

    plt.ylabel('best fitness')
    plt.xlabel('delay [ms]')
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
