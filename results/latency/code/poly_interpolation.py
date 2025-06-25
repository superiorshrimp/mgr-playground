import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import Polynomial

# Hardcoded data from the graph
x = np.array([5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80])
y = np.array([0.21, 0.31, 0.34, 0.46, 0.71, 0.95, 1.10, 1.48, 1.65, 2.64, 3.54, 4.86, 6.60, 7.87, 13.22, 23.33])

# Fit a polynomial of chosen degree (e.g., degree 3 or 4)
degree = 3
coeffs = np.polyfit(x, y, degree)
p = np.poly1d(coeffs)

# Generate dense x-values for smooth interpolation curve
x_dense = np.linspace(min(x), max(x), 300)
y_dense = p(x_dense)

# Plot original points and interpolation
plt.plot(x, y, 'o', label='Original Data')
plt.plot(x_dense, y_dense, '-', label=f'{degree}° Polynomial Fit')
plt.xlabel('islands')
plt.ylabel('time [ms]')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Optionally print polynomial
print("Polynomial coefficients (highest degree first):")
print(coeffs)
