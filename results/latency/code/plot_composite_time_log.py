import os
from math import inf
import numpy as np
from matplotlib import pyplot as plt

HISTORY_PATH = 'history/'

def main():
    times = []
    # with open(HISTORY_PATH + "t_success.txt", 'r') as f:
    with open(HISTORY_PATH + "t_fail.txt", 'r') as f:
    # with open(HISTORY_PATH + "h.txt", 'r') as f:
    # with open(HISTORY_PATH + "hr.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            times.append(1000*float(line))

    x_vals = [5 * (i + 1) for i in range(len(times))]

    plt.plot(x_vals, times, marker='o')

    for x, y in zip(x_vals, times):
        plt.text(x, y, f'{y:.2f}', ha='center', va='bottom', fontsize=8)

    plt.xticks(x_vals)
    plt.ylabel('time [ms]')
    plt.xlabel('islands')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
