from matplotlib import pyplot as plt
import numpy as np
import json


FROM = 1990
TO = 1996
STEP = 1
PATH_BASE = "logs\\"

def get_y(file_name):
    f = open(file_name)
    j = json.load(f)

    return np.array(
        [j[str(i)] for i in range(FROM, TO)]
    )

x = np.arange(FROM, TO, STEP)
y = [
    get_y(PATH_BASE + "240426\Rast200\g205440 3rk-co5ilu5\\resultsEveryStepW0.json"),
    get_y(PATH_BASE + "240426\Rast200\g212216 3rk-co5ilu5\\resultsEveryStepW0.json"),
    get_y(PATH_BASE + "240426\Rast200\g212537 3rk-co5ilu5\\resultsEveryStepW0.json"),
    get_y(PATH_BASE + "240426\Rast200\g212730 3rk-co5ilu5\\resultsEveryStepW0.json"),
    get_y(PATH_BASE + "240426\Rast200\g212912 3rk-co5ilu5\\resultsEveryStepW0.json"),
    get_y(PATH_BASE + "240426\Rast200\g213019 3rk-co5ilu5\\resultsEveryStepW0.json")
]

plt.plot(x, y[0], label='5,5')
plt.plot(x, y[1], label='0,0')
plt.plot(x, y[2], label='5,0')
plt.plot(x, y[3], label='0,5')
plt.plot(x, y[4], label='5,5')
plt.plot(x, y[5], label='8,8')

plt.legend()
plt.show()
