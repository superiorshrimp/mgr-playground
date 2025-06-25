import os
import re

RESULTS_PATH = 'results/latency-blocking/'

fitness_pattern = re.compile(r"Fitness:\s+([0-9]*\.?[0-9]+)")

for filename in os.listdir(RESULTS_PATH):
    if filename.startswith('slurm-'):
        fitness_values = []

        with open(RESULTS_PATH + filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if "Fitness: " in line:
                    match = fitness_pattern.search(line)
                    if match:
                        # if filename == "slurm-b1d55-1": print(line)
                        fitness_values.append(match.group(1))

        if fitness_values:
            suffix = filename[len('slurm-'):]
            out_filename = f"g-{suffix}"

            with open(RESULTS_PATH + out_filename, 'w') as out_file:
                out_file.write("\n".join(fitness_values) + "\n")
