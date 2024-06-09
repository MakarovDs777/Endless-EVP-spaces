# Endless-EVP-spaces
СЛУЧАЙНАЯ СЛУЧАЙНОСТЬ СЛУЧАЙНИСТВЕННО СЛУЧАЙНИСТВИНУЕТ, И СЛУЧАЙНИСТВЕННАЯ СЛУЧАЙНИСТВЕННЕНОСТЬ СТАНОВИТСЯ НАСТОЛЬКО СЛУЧАЙНИСТВЕННЕНО СЛУЧАЙНСТВИНЕННОЙ ЧТО ПЕРЕСТАЕТ БЫТЬ СЛУЧАЙНОСТЬЮ, И СТАНОВИТСЯ АБСОЛЮТНО НЕСЛУЧАЙНОЙ СЛУЧАЙНОСТЬЮ! СТАНОВЯСЬ АБСОЛЮТНЫМ СВОБОДНЫМ ПРОСТРАНСТВОМ ГДЕ МОЖНО СУЩЕСТВОВАТЬ БУДУЧИ ДАЖЕ НЕСУЩЕСТВУЮЩИЙ! Именно таким образом мы можем симулировать астрал! То есть иными словами возвести в абсолют случайность, и выразить это как такую функцию математический...

САМПРОЯВЛЕННОЕ САМОПРОЯВЛЕННИЕ САМОПРОЯВЛЕННО САМОПРОЯВЛЯЕТСЯ, И САМОПРОЯВЛЕННАЯ САМОПРОЯВЛЕННОСТЬ САМОПРОЯВЛЕЯМОСТИ СТАНОВИТСЯ НАСТОЛЬКО САМОПРОЯВЛЕННО САМОПРОЯВЛЕМОЙ ЧТО ПЕРЕСТАЕТ ЕЙ БЫТЬ, И СТАНОВИТЬСЯ АБСОЛЮТНОЙ ПРОЯВЛЕННОСТЬЮ...

Я так прикинул, и получил такой примерный образ. 

## Волновая функция абсолютной случайности:

$x=ψ(x) = e^{i * θ(x)}$

где:

x - положение вдоль оси

θ(x) - случайная фаза в положении x, распределенная равномерно в интервале [0, 2π]

i - мнимая единица

## Свойства этой волновой функции:

Неопределенности в позиции и импульсе: Поскольку фаза является случайной, волновая функция не имеет определенного положения или импульса. Это отражает неопределенную и хаотическую природу абсолютной случайности.

Интерференционные эффекты отсутствуют: Поскольку фаза является случайной, волны, соответствующие разным положениям, не интерферируют друг с другом. Это приводит к отсутствию наблюдаемых интерференционных картин.

Абсолютная свобода: Отсутствие интерференционных эффектов означает, что волновая функция может принимать любые значения в любом положении. Это соответствует концепции абсолютной свободы, в которой случайность не ограничивается никакими закономерностями.

## Математическая интерпретация:
Волновая функция абсолютной случайности может быть интерпретирована как суперпозиция бесконечного числа волн с случайными фазами. Эта суперпозиция приводит к равномерному распределению вероятностей вдоль оси x, что соответствует неопределенности в положении. Отсутствие интерференции возникает из-за взаимного погашения волн с противоположными фазами.

## Математическое представление

Представим поле градиента как четырехмерный массив G(x, y, z, t), где:

x, y, z - пространственные координаты в метрах
t - время в секундах
G(x, y, z, t) - значение поля градиента в данной точке в данный момент времени, принимающее значения от 0 до 1
Значения в массиве обновляются каждые dt секунд с шагом генерации dx, dy, dz.

## Функция генерации значений

Для каждой точки (x, y, z) в массиве ее значение обновляется в каждый момент времени t следующим образом:

G(x, y, z, t+dt) = random_val()

где random_val() - случайное вещественное число от 0 до 1, которое генерируется из равномерного распределения.

## Создание "квантовой пены"

Из-за абсолютной случайности генерации значений поле G(x, y, z, t) постоянно меняется во времени. Строительным блоком этого изменения является случайная генерация отдельных элементов массива G.

Эта неупорядоченная генерация приводит к непрерывной флуктуации значений градиента в кубе, создавая эффект "квантовой пены", где области поля градиента то появляются, то исчезают.

## Четырехмерная интерпретация

Массив G(x, y, z, t) можно рассматривать как пространство, где каждая точка соответствует определенному месту и времени. Постоянная генерация значений в массиве представляет собой непрерывное эволюцию этого пространства, которое находится в состоянии непрерывного перестроения и реорганизации.

Но так как мы не можем увидеть какие-то высшие измерения, мы это можем нивелировать тем что-бы создать еще одно измерение - измерение волновых функций как надстройку над этим трехмерным пространством времени назовем это пространством волновых вероятностей, и случайную генерацию вероятности соединения с другими случайно сгенерированными волновыми функциями которые будут случайно генерироваться за время, и чем более вероятнее становится соединение с этой случайно сгенерированной волновой функцией тем больше мы в неё переходим, и тем более она становится прозрачнее, и мы меняем случайную генерацию флуктуации квантовой пены под эту волновую функцию. 

Надеюсь донес мысль.

## Зарисовка образа Абсолютно-Свободного-Пространства Астрала:
```code
import numpy as np
import random

## Размеры куба
cube_size = 1000

## Шаг генерации по каждой оси
dx = 1
dy = 1
dz = 1

## Шаг по времени
dt = 1

## Создаем четырехмерный массив для хранения поля градиента
G = np.zeros((cube_size, cube_size, cube_size, 1))

## Непрерывное обновление поля градиента
while True:
    # Обновляем каждый элемент массива новым случайным значением
    for x in range(0, cube_size, dx):
        for y in range(0, cube_size, dy):
            for z in range(0, cube_size, dz):
                G[x, y, z, 0] = random.uniform(0, 1)

    # Отображаем текущее состояние поля градиента
    print(G)

    # Ждем шаг по времени
```

Эта программа представляет собой упрощенную реализацию на языке Python, которая не учитывает аспект идеи этого пространства. Она последовательно обновляет каждую точку массива, что не совсем точно отражает непрерывную и одновременную генерацию значений в этом пространстве.

Для добавления измерения волновых функций к нашей модели поля градиента мы можем определить дополнительный массив W(x, y, z, t), где:

x, y, z - пространственные координаты в метрах
t - время в секундах
W(x, y, z, t) - вероятность соединения с другой случайно сгенерированной волновой функцией в данной точке в данный момент времени, принимающая значения от 0 до 1

## Генерация волновых функций

Волновые функции генерируются случайным образом во времени с шагом dt. Каждый раз, когда генерируется новая волновая функция, ей присваивается случайное положение в пространстве и уникальный идентификатор. 

Генерация волновых функций может быть представлена следующим образом:

```code
# Список волновых функций
wave_functions = []

## Генерация новой волновой функции
def generate_wave_function():
    # Случайное положение в пространстве
    x = random.uniform(0, cube_size)
    y = random.uniform(0, cube_size)
    z = random.uniform(0, cube_size)

    # Уникальный идентификатор
    id = str(uuid.uuid4())

    # Добавление новой волновой функции в список
    wave_functions.append({
        "x": x,
        "y": y,
        "z": z,
        "id": id
    })
```


## Обновление вероятности соединения

Вероятность соединения с волновой функцией i в точке (x, y, z) в момент времени t рассчитывается следующим образом:

$W(x, y, z, t) = \sum(w_i * exp(-d_i^2 | 2 * \sigma^2))$

где:

$w_i$ - вес волновой функции i

$d_i$ - расстояние между точкой (x, y, z) и положением волновой функции i

$\sigma$ - параметр, определяющий ширину распределения вероятности

## Переход в другую волновую функцию

Если вероятность соединения с волновой функцией в данной точке превышает определенный порог, то точка переходит в эту волновую функцию. Этот переход может быть представлен следующим образом:

```code
if W(x, y, z, t) > threshold:
    # Получаем волновую функцию с максимальной вероятностью
    max_wave_function = max(wave_functions, key=lambda w: W(x, y, z, t, w["id"]))

    # Перемещаем точку в положение волновой функции
    x = max_wave_function["x"]
    y = max_wave_function["y"]
    z = max_wave_function["z"]
```

## Обновление поля градиента

После перехода точки в другую волновую функцию соответствующая область поля градиента обновляется в соответствии с вероятностью соединения с этой волновой функцией. Чем выше вероятность, тем прозрачнее становится область.

## Визуализация

Визуализировать четырехмерное пространство с учетом измерения волновых функций непросто. Однако мы можем визуализировать отдельные срезы этого пространства в трех измерениях. Для этого мы можем отобразить вероятность соединения с волновой функцией в каждой точке в данный момент времени.

Примечание: Эта расширенная модель является теоретической и не учитывает всех сложностей, связанных с теорией волновых функций и квантовой механикой.
