import os
import re

# Set your target directory here
directory = "."

# Regex pattern: matches slurm-c0.10d10-3, slurm-c1.00d0-4, etc.
pattern = re.compile(r"^slurm-c([0-9]+\.[0-9]+)d(0|5|10)-([0-4])$")

for filename in os.listdir(directory):
    match = pattern.match(filename)
    if match:
        c_value, d_value, index = match.groups()

        # Keep 1.0 and 0.0 as-is; otherwise strip trailing zeros
        if c_value in ('1.0', '0.0'):
            c_cleaned = c_value
        else:
            c_cleaned = str(float(c_value)).rstrip('0').rstrip('.') if '.' in c_value else c_value

        new_filename = f"slurm-c{c_cleaned}d{d_value}-{index}"
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_filename)

        if filename != new_filename:
            print(f"Renaming: {filename} -> {new_filename}")
            os.rename(old_path, new_path)