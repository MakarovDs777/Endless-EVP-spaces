"""import numpy as np
from mayavi import mlab
from qutip import destroy, thermal_dm
import time

# Параметры системы
N = 20  # Размерность пространства состояний
n_th = 0.5  # Температура

# Операторы рождения и уничтожения
a = destroy(N)

# Начальное состояние системы (термодинамическое)
rho0 = thermal_dm(N, n_th)

# Создание сцены Mayavi
fig = mlab.figure(size=(800, 600))

# Создание трехмерной сетки куба
x, y, z = np.mgrid[0:10:N*1j, 0:10:N*1j, 0:10:N*1j]

# Создание начального состояния системы
state = np.abs((a.dag() * a * rho0).tr())  # Ожидаемое значение оператора числа

# Создание объекта-сетки для визуализации
grid = mlab.pipeline.scalar_field(x, y, z, state)
mlab.pipeline.volume(grid)

# Функция обновления в реальном времени
def update_figure():
    while True:
        state = np.abs((a.dag() * a * rho0).tr())  # Ожидаемое значение оператора числа
        grid.mlab_source.scalars = state
        time.sleep(0.1)

# Запуск функции обновления в реальном времени
update_figure()

# Отображение сцены
mlab.show()"""

import numpy as np
from mayavi import mlab
import random

def V(x, y, z):
    return np.cos(10*x) + np.cos(10*y) + np.cos(10*z) + 2*(x**2 + y**2 + z**2)

# Parameters
grid_size = 100
time_step = 0.1
fluctuation_size = 0.2
fluctuation_amplitude = 1.0
fluctuation_lifetime = 5

# инициализация
X, Y, Z = np.mgrid[-2:2:100j, -2:2:100j, -2:2:100j]
V = np.zeros((grid_size, grid_size, grid_size))
t = 0

# Цикл вечный
while True:
    # Генерировать случайные флуктуации
    num_fluctuations = random.randint(10, 20)
    for i in range(num_fluctuations):
        # Выберите случайную точку
        x = random.uniform(-2, 2)
        y = random.uniform(-2, 2)
        z = random.uniform(-2, 2)

        #Сгенерируйте случайный вектор
        vx = random.uniform(-fluctuation_amplitude, fluctuation_amplitude)
        vy = random.uniform(-fluctuation_amplitude, fluctuation_amplitude)
        vz = random.uniform(-fluctuation_amplitude, fluctuation_amplitude)
        v = np.array([vx, vy, vz])

        # Добавьте флуктуацию к векторному полю
        V[int((x - (-2))/(4/grid_size)):int((x - (-2))/(4/grid_size)) + int(fluctuation_size*grid_size),
          int((y - (-2))/(4/grid_size)):int((y - (-2))/(4/grid_size)) + int(fluctuation_size*grid_size),
          int((z - (-2))/(4/grid_size)):int((z - (-2))/(4/grid_size)) + int(fluctuation_size*grid_size)] += v

    # сглаживание
    V = ndimage.gaussian_filter(V, sigma=0.5)

    # Затухание флуктуаций
    V *= np.exp(-t / fluctuation_lifetime)

    # Время обновления
    t += time_step

    # Визуализация
    mlab.contour3d(X, Y, Z, V)
