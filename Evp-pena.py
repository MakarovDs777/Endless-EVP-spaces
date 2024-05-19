import numpy as np
import matplotlib.pyplot as plt
from qutip import basis, qeye, destroy, mesolve, thermal_dm

# Параметры системы
N = 20  # Размерность пространства состояний
n_th = 0.5  # Температура

# Операторы рождения и уничтожения
a = destroy(N)
n = a.dag() * a

# Гамильтониан
H = a.dag() * a

# Начальное состояние системы (термодинамическое)
rho0 = thermal_dm(N, n_th)

# Список временных точек
tlist = np.linspace(0, 10, 100)

# Расчет динамики системы
result = mesolve(H, rho0, tlist, [], [n])

# Визуализация результатов (график)
plt.plot(tlist, result.expect[0])
plt.xlabel('Время')
plt.ylabel('Ожидаемое значение оператора числа')
plt.show()
