from enthought.mayavi import mlab
import numpy as np

def V(x, y, z):
    return np.cos(10*x)*np.cos(10*y)*np.cos(10*z) +2*(x**2+y**2+z**2)

X, Y, Z = np.mgrid[-2:2:100j, -2:2:100j, -2:2:100j]

mlab.contour3d(X, Y, Z, V)
