import glob

def compute_avg_from_file(filename):
    try:
        with open(filename) as f:
            values = []
            for line in f:
                if "migration_time" in line:
                # if "evo_step_time" in line:
                    parts = line.split()
                    if len(parts) >= 6:
                        try:
                            values.append(float(parts[5])) # migration_time parts[4] & evo_step_time parts[5]
                        except ValueError:
                            pass
            if values:
                avg = sum(values) / len(values)
                return f"{avg:.10f}"
            else:
                return "NaN"
    except FileNotFoundError:
        return "file not found"

# Loop over matching files
for file in glob.glob("results/selection/slurm-c*d0-*"):
    avg = compute_avg_from_file(file)
    print(f"{file} average={avg}")
