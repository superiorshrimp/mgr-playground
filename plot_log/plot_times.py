from matplotlib import pyplot as plt

def main():
    with open("history/t.json", "r") as f:
        lines = f.readlines()
        d = {}
        for line in lines:
            if len(line) < 5:
                continue
            split = line.split(" ")
            print(split)
            d[int(split[0])] = (float(split[1]), float(split[2]))

    for i in range(len(d.keys())):
        plt.plot([i,i], d[i])
    plt.show()

if __name__ == "__main__":
    main()