import os
from math import inf
import numpy as np
from matplotlib import pyplot as plt
import re

RESULTS_PATH = 'results/selection/maxfit_0-1/'
RESULTS_PATH = 'results/selection/maxfit/'
# RESULTS_PATH = 'results/selection/sndev/'

def main():
    y_values = {}
    coef_values = set()

    for filename in os.listdir(RESULTS_PATH):
        if filename.startswith('g-'):
            filename_pattern = re.compile(r"g-c(.+)d(\d+)-\d+")

            match = filename_pattern.search(filename)

            coef_val = float(match.group(1))
            d_val = int(match.group(2))

            # if d_val < 0.4:
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

    def flatten_and_sort(data_dict):
        x = []
        y = []
        for d in sorted(data_dict.keys()):
            values = data_dict[d]
            x.extend([d] * len(values))
            y.extend(values)
        return np.array(x), np.array(y)

    y_values_flattened = {}
    for d_key in sorted(y_values.keys()):
        y_values_flattened[d_key] = []
        for coef_key in sorted(coef_values):
            y_values_flattened[d_key].append(y_values[d_key][coef_key])

    y_trend_lines = {}
    for d_key in sorted(y_values.keys()):
        y_trend_lines[d_key] = flatten_and_sort(y_values[d_key])
        plt.scatter(y_trend_lines[d_key][0], y_trend_lines[d_key][1], label='delay='+str(d_key), alpha=0.7)

    for x, y, label, data_dict in [
        (y_trend_lines[d_key][0],
        y_trend_lines[d_key][1],
        'delay_=' + str(d_key),
        y_values_flattened[d_key])
        for d_key in sorted(y_values.keys())
    ]:
        # print(x, y, label, data_dict)
        # print(x,y)
        coeffs = np.polyfit(x, y, deg=2)
        print(f"Coefficients for {label}: {coeffs}")

        poly_function = np.poly1d(coeffs)

        x_trend = np.linspace(min(x), max(x), 200)

        y_trend = poly_function(x_trend)

        plt.plot(x_trend, y_trend, linestyle='--')
        # plt.plot(x_trend, y_trend, linestyle='--', label=f'{label} trend (2nd deg fit)')

    # def plot_min_max_band(y_dict, color):
    #     min_vals = []
    #     max_vals = []
    #     x_unique = sorted(y_dict.keys())
    #     for d in x_unique:
    #         vals = y_dict[d]
    #         if vals:
    #             min_vals.append(min(vals))
    #             max_vals.append(max(vals))
    #         else:
    #             min_vals.append(np.nan)
    #             max_vals.append(np.nan)
    #
    #     min_vals = np.array(min_vals)
    #     max_vals = np.array(max_vals)
    #     x_unique = np.array(x_unique)
    #
    #     plt.fill_between(x_unique, min_vals, max_vals, color=color, alpha=0.2)
    #
    # plot_min_max_band(y_values_b0, 'blue')
    # plot_min_max_band(y_values_b1, 'orange')

    plt.ylabel('best fitness')
    plt.xlabel('delay [ms]')
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()