import numpy as np
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
mlab.show()
