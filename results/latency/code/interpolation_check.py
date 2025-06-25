import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# Dane z wykresu na podstawie odczytu punktów (oszacowane z obrazu)
x_data = np.array([5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80])
y_data = np.array([0.31, 0.21, 0.24, 0.46, 0.71, 0.95, 1.0, 1.48, 1.85, 2.64, 3.4, 4.8, 6.6, 7.87, 13.02, 23.33])

# Definicje funkcji dopasowania
def poly2(x, a, b, c):
    return a * x**2 + b * x + c

def poly3(x, a, b, c, d):
    return a * x**3 + b * x**2 + c * x + d

def poly4(x, a, b, c, d, e):
    return a * x**4 + b * x**3 + c * x**2 + d * x + e

def exp_func(x, a, b, c):
    return a * np.exp(b * x) + c

# Dopasowanie modeli
params_poly2, _ = curve_fit(poly2, x_data, y_data)
params_poly3, _ = curve_fit(poly3, x_data, y_data)
params_poly4, _ = curve_fit(poly4, x_data, y_data)
params_exp, _ = curve_fit(exp_func, x_data, y_data, maxfev=10000)

# Wartości dopasowane
x_fit = np.linspace(min(x_data), max(x_data), 300)
y_poly2 = poly2(x_fit, *params_poly2)
y_poly3 = poly3(x_fit, *params_poly3)
y_poly4 = poly4(x_fit, *params_poly4)
y_exp = exp_func(x_fit, *params_exp)

# Wykres porównawczy
plt.figure(figsize=(10, 6))
plt.scatter(x_data, y_data, label="Dane oryginalne", color='black')
plt.plot(x_fit, y_poly2, label="Dopasowanie kwadratowe", linestyle='--')
plt.plot(x_fit, y_poly3, label="Dopasowanie sześcienne", linestyle='-.')
plt.plot(x_fit, y_poly4, label="Dopasowanie wielomianem stopnia czwartego", linestyle='-.')
# plt.plot(x_fit, y_exp, label="Dopasowanie wykładnicze", linestyle=':')
plt.xlabel("islands")
plt.ylabel("time [ms]")
plt.title("Porównanie dopasowań modeli")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
