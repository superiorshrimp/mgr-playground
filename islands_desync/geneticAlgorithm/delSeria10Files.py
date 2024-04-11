import os
import sys

data = sys.argv[1]
probl = sys.argv[2]
dim = sys.argv[3]

probl_dim = probl + dim

print(data, probl_dim)

filesPaths = [
    "logs/" + data + "/" + probl_dim + "/seriaEnd0.txt",
    "logs/" + data + "/" + probl_dim + "/seriaEnd1.txt",
    "logs/" + data + "/" + probl_dim + "/seriaEnd2.txt",
    "logs/" + data + "/" + probl_dim + "/seriaEnd3.txt",
    "logs/" + data + "/" + probl_dim + "/seriaEnd4.txt",
    "logs/" + data + "/" + probl_dim + "/seriaEnd5.txt",
    "logs/" + data + "/" + probl_dim + "/seriaEnd6.txt",
    "logs/" + data + "/" + probl_dim + "/seriaEnd7.txt",
    "logs/" + data + "/" + probl_dim + "/seriaEnd8.txt",
    "logs/" + data + "/" + probl_dim + "/seriaEnd9.txt",
]

for i in range(10):
    if os.path.exists(filesPaths[i]):
        os.remove(filesPaths[i])
        print("Successfully! The File " + filesPaths[i] + " has been removed")
    else:
        print("Can not delete the file" + filesPaths[i] + " as it doesn't exists")

print("end delSeria10Files")
