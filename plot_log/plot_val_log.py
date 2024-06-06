from matplotlib import pyplot as plt
import numpy as np
import json


FROM = 1990
TO = 1996
STEP = 1
PATH_BASE = "logs/"

def get_y(file_name):
    f = open(file_name)
    j = json.load(f)

    return np.array(
        [j[str(i)] for i in range(FROM, TO)]
    )

x = np.arange(FROM, TO, STEP)
y = [
    get_y(PATH_BASE + "240427/Rast200/g115954 3rk-co9999ilu0/resultsEveryStepW0.json"),
    get_y(PATH_BASE + "240427/Rast200/g120144 3rk-co5ilu5/resultsEveryStepW0.json"),
    get_y(PATH_BASE + "240427/Rast200/g120249 3rk-co2ilu5/resultsEveryStepW0.json"),
    get_y(PATH_BASE + "240427/Rast200/g120355 3rk-co5ilu2/resultsEveryStepW0.json"),
    get_y(PATH_BASE + "240427/Rast200/g120450 3rk-co8ilu8/resultsEveryStepW0.json"),
    get_y(PATH_BASE + "240427/Rast200/g121656 3bk-co8ilu8/resultsEveryStepW0.json"),
]

plt.plot(x, y[0], label='0,9999')
plt.plot(x, y[1], label='5,5')
plt.plot(x, y[2], label='5,2')
plt.plot(x, y[3], label='2,5')
plt.plot(x, y[4], label='8,8')
plt.plot(x, y[5], label='8,8')

plt.legend(loc='upper right')
plt.show()
