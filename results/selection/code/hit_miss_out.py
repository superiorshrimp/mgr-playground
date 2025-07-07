import os

RESULTS_PATH = 'results/selection/'

for filename in os.listdir(RESULTS_PATH):
    if filename.startswith('slurm-'):

        hit = 0
        miss = 0
        get_success = 0
        with open(RESULTS_PATH + filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if "HIT" in line:
                    hit += 1
                if "MISS" in line:
                    miss += 1
                if "get_time_success" in line:
                    get_success += 1

        suffix = filename[len('slurm-'):]
        out_filename = f"hm-{suffix}"

        with open(RESULTS_PATH + out_filename, 'w') as out_file:
            out_file.write(str(hit))
            out_file.write("\n")
            out_file.write(str(miss))
            out_file.write("\n")
            out_file.write(str(get_success))
