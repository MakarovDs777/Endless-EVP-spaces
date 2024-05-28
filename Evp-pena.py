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
from enthought.mayavi import mlab
import random

def V(x, y, z):
    return np.cos(10*x) + np.cos(10*y) + np.cos(10*z) + 2*(x**2 + y**2 + z**2)

# Параметры
размер_сетки = 100
шаг_по_времени = 0,1
размер_флуктуации = 0,2
амплитуда_флуктуации = 1,0
время_жизни_флуктуации = 5

# Инициализация
X, Y, Z = np.mgrid[-2:2:100j, -2:2:100j, -2:2:100j]
V = np.zeros((размер_сетки, размер_сетки, размер_сетки))
время = 0

# Цикл времени
while True:
    # Сгенерировать случайные флуктуации
    количество_флуктуаций = random.randint(10, 20)
    для i в range(количество_флуктуаций):
        # Выбрать случайную точку
        x = random.uniform(-2, 2)
        y = random.uniform(-2, 2)
        z = random.uniform(-2, 2)

        # Сгенерировать случайный вектор
        vx = random.uniform(-амплитуда_флуктуации, амплитуда_флуктуации)
        vy = random.uniform(-амплитуда_флуктуации, амплитуда_флуктуации)
        vz = random.uniform(-амплитуда_флуктуации, амплитуда_флуктуации)
        v = np.array([vx, vy, vz])

        # Добавить флуктуацию к векторному полю
        V[int((x - (-2))/(4/размер_сетки)):int((x - (-2))/(4/размер_сетки)) + размер_флуктуации*размер_сетки,
          int((y - (-2))/(4/размер_сетки)):int((y - (-2))/(4/размер_сетки)) + размер_флуктуации*размер_сетки,
          int((z - (-2))/(4/размер_сетки)):int((z - (-2))/(4/размер_сетки)) + размер_флуктуации*размер_сетки] += v

    # Размытие
    V = ndimage.gaussian_filter(V, sigma=0.5)

    # Уменьшение флуктуаций
    V *= np.exp(-время / время_жизни_флуктуации)

    # Обновление времени
    время += шаг_по_времени

    # Визуализация
    mlab.contour3d(X, Y, Z, V)
