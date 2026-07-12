import numpy as np

p1 = np.array([-248.1344, -56.06006, 0.0])
p2 = np.array([-245.4237, -51.16113, 3.702135])

v = p2-p1

dx, dy, dz = v[0], v[1], v[2]


if dx != 0 or dy != 0:
    wx, wy, wz = -dy, dx, 0.0
else:
    wx, wy, wz = 1.0, 0.0, 0.0
    

norm = (wx**2 + wy**2 + wz**2) ** 0.5
wx, wy, wz = wx / norm, wy / norm, wz / norm

length = 1.0
x3 = p1[0] + length * wx
y3 = p1[1] + length * wy
z3 = p1[2] + length * wz

print(x3, y3, z3)