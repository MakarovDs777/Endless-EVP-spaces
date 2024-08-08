import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import noise

# Инициализация Pygame
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

# Инициализация камеры
gluPerspective(45, (display[0]/display[1]), 0.1, 1000.0)
glTranslatef(0.0, 0.0, -30)
glRotatef(45, 1, 0, 0)  # Повернуть камеру на 45 градусов вокруг оси X

# Параметры шума Перлина
octaves = 4
persistence = 0.5
lacunarity = 2

# Создание 3D-массива шума Перлина
shape = (32, 32, 32)

# Нормализация шума в диапазон от 0 до 1
def normalize_noise(noise):
    return (noise - noise.min()) / (noise.max() - noise.min())

# Генерация шума Перлина для одного кадра
def generate_noise(base, scale):
    noise = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                noise[i][j][k] = noise.pnoise3(i/scale,
                                              j/scale,
                                              k/scale,
                                              octaves=octaves,
                                              persistence=persistence,
                                              lacunarity=lacunarity,
                                              repeatx=shape[0],
                                              repeaty=shape[1],
                                              repeatz=shape[2],
                                              base=int(base))
    return normalize_noise(noise)

# Создание террейна
def create_terrain(width, height, x_offset, z_offset, base, scale):
    noise_map = generate_noise(base, scale)
    vertices = []
    for i in range(width):
        for j in range(height):
            x = i - width // 2
            z = j - height // 2
            y = noise_map[i][j][0] * 10
            vertices.append((x + x_offset, y, z + z_offset))
    return vertices

# Отрисовка террейна
def draw_terrain(vertices, width, height):
    glBegin(GL_LINES)
    for i in range(width):
        for j in range(height):
            if i < width - 1:
                glVertex3fv(vertices[i * height + j])
                glVertex3fv(vertices[(i + 1) * height + j])
            if j < height - 1:
                glVertex3fv(vertices[i * height + j])
                glVertex3fv(vertices[i * height + j + 1])
    glEnd()

# Основной цикл
width, height = 32, 32
x_offset = 0
z_offset = 0
base = 0
scale = 10
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                z_offset += 5
            if event.key == pygame.K_s:
                z_offset -= 5
            if event.key == pygame.K_a:
                x_offset -= 5
            if event.key == pygame.K_d:
                x_offset += 5

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    base += 1
    vertices = create_terrain(width, height, x_offset, z_offset, base, scale)
    draw_terrain(vertices, width, height)
    pygame.display.flip()
    clock.tick(60)
