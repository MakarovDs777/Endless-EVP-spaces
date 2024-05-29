import numpy as np
from mayavi import mlab

def V(x, y, z):
    return np.cos(10*x)*np.cos(10*y)*np.cos(10*z) + 2*(x**2 + y**2 + z**2)

X, Y, Z = np.mgrid[-2:2:100j, -2:2:100j, -2:2:100j]

mlab.contour3d(X, Y, Z, V, contours=10)  # Установите количество контуров

mlab.show() 
