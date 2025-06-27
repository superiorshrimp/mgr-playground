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

    plt.scatter(x_b0, y_b0, label='non-blocking', alpha=0.7)
    plt.scatter(x_b1, y_b1, label='blocking', alpha=0.7)

    for x, y, color, label, data_dict in [(x_b0, y_b0, 'blue', 'non-blocking', y_values_b0),
                                          (x_b1, y_b1, 'orange', 'blocking', y_values_b1)]:
        coeffs = np.polyfit(x, y, deg=2)
        print(f"Coefficients for {label}: {coeffs}")

        poly_function = np.poly1d(coeffs)

        x_trend = np.linspace(min(x), max(x), 200)

        y_trend = poly_function(x_trend)

        plt.plot(x_trend, y_trend, color=color, linestyle='--', label=f'{label} trend (2nd deg fit)')

    def plot_min_max_band(y_dict, color):
        min_vals = []
        max_vals = []
        x_unique = sorted(y_dict.keys())
        for d in x_unique:
            vals = y_dict[d]
            if vals:
                min_vals.append(min(vals))
                max_vals.append(max(vals))
            else:
                min_vals.append(np.nan)
                max_vals.append(np.nan)

        min_vals = np.array(min_vals)
        max_vals = np.array(max_vals)
        x_unique = np.array(x_unique)

        plt.fill_between(x_unique, min_vals, max_vals, color=color, alpha=0.2)

    plot_min_max_band(y_values_b0, 'blue')
    plot_min_max_band(y_values_b1, 'orange')

    plt.ylabel('best fitness')
    plt.xlabel('delay [ms]')
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()