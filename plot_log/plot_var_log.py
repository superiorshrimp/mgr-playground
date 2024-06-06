from matplotlib import pyplot as plt
import numpy as np
import json


FROM = 1
TO = 1996
STEP = 1
PATH_BASE = "logs/"

def get_v(file_name):
    f = open(file_name)
    j = json.load(f)

    return np.array(
        [j[str(i)]["y3"] for i in range(FROM, TO)]
    )

x = np.arange(FROM, TO, STEP)
y = [
    get_v(PATH_BASE + "240427/Rast200/g115954 3rk-co9999ilu0/W0 set-minOS-srOS-diversity.json"),
    get_v(PATH_BASE + "240427/Rast200/g120144 3rk-co5ilu5/W0 set-minOS-srOS-diversity.json"),
    get_v(PATH_BASE + "240427/Rast200/g120249 3rk-co2ilu5/W0 set-minOS-srOS-diversity.json"),
    get_v(PATH_BASE + "240427/Rast200/g120355 3rk-co5ilu2/W0 set-minOS-srOS-diversity.json"),
    get_v(PATH_BASE + "240427/Rast200/g120450 3rk-co8ilu8/W0 set-minOS-srOS-diversity.json"),
]

plt.plot(x, y[0], label='0,9999')
plt.plot(x, y[1], label='5,5')
plt.plot(x, y[2], label='5,2')
plt.plot(x, y[3], label='2,5')
plt.plot(x, y[4], label='8,8')

plt.legend(loc='upper right')
plt.show()
