import os
from math import inf
import numpy as np
from matplotlib import pyplot as plt

HISTORY_PATH = 'history/'

def main():
    times_success = []
    with open(HISTORY_PATH + "t_success.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            times_success.append(1000*float(line))

    times_fail = []
    with open(HISTORY_PATH + "t_fail.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            times_fail.append(1000*float(line))

    ratios = [
        times_success[i]/(times_success[i] + times_fail[i])
        for i in range(len(times_success))
    ]

    x_vals = [5 * (i + 1) for i in range(len(ratios))]

    plt.plot(x_vals, ratios, marker='o')

    for x, y in zip(x_vals, ratios):
        plt.text(x, y, f'{y:.2f}', ha='center', va='bottom', fontsize=8)

    plt.xticks(x_vals)
    plt.ylabel('IO duration / request duration')
    plt.xlabel('islands')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
