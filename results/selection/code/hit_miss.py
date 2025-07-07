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
        if filename.startswith('hm-'):
            filename_pattern = re.compile(r"hm-c(.+)d(\d+)-\d+")

            match = filename_pattern.search(filename)

            coef_val = match.group(1)
            d_val = int(match.group(2))

            if coef_val < "0.4":
                continue

            coef_values.add(coef_val)

            file_path = RESULTS_PATH + filename

            hit = None
            miss = None
            get_success = None
            with open(file_path, 'r') as f:
                c = 0
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        if c == 0:
                            hit = int(line)
                            c += 1
                        elif c == 1:
                            miss = int(line)
                            c += 1
                        else:
                            get_success = int(line)
                    except (ValueError, IndexError):
                        continue

            if y_values.get(d_val, None) is None:
                y_values[d_val] = {}
            if y_values[d_val].get(coef_val, None) is None:
                y_values[d_val][coef_val] = [hit]
                # y_values[d_val][coef_val] = [hit/get_success]
            else:
                y_values[d_val][coef_val].append(hit)
                # y_values[d_val][coef_val].append(hit/get_success)

    avg_y_values = {}
    for d_key in sorted(y_values.keys()):
        avg_y_values[d_key] = []
        for coef_key in sorted(coef_values):
            avg_y_values[d_key].append(np.mean(y_values[d_key][coef_key]))

    for d_key in sorted(y_values.keys()):
        plt.plot(avg_y_values[d_key], label='delay = ' + str(d_key), alpha=0.7)

    x_vals = list(coef_values)
    plt.xticks(ticks=[_ for _ in range(len(x_vals))], labels=sorted(x_vals))
    plt.ylabel('hit count')
    plt.xlabel('delay [ms]')
    plt.tight_layout()
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
