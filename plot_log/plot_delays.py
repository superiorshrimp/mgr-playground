import json
import os
from matplotlib import pyplot as plt

def main():
    files = os.listdir("history")
    json_objs = []
    for file in files:
        if os.path.isfile("history/" + file):
            if file.endswith(".json") and file.startswith("w"):
                json_objs.append(
                    json.load(open("history/" + file))
                )
    delays = []
    for obj in json_objs:
        for key, value in obj.items():
            from_timestamps = value["timestamps"]
            to_timestamp = value["destinTimestamp"]
            for from_timestamp in from_timestamps:
                delays.append(to_timestamp - from_timestamp)

    plt.hist(delays, bins=100)
    plt.show()

if __name__ == "__main__":
    main()