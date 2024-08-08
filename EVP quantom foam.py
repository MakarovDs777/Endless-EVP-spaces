import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import noise
from skimage import measure

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
    noise_array = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            for k in range(shape[2]):
                noise_array[i][j][k] = noise.pnoise3(i/scale,
                                              j/scale,
                                              k/scale,
                                              octaves=octaves,
                                              persistence=persistence,
                                              lacunarity=lacunarity,
                                              repeatx=shape[0],
                                              repeaty=shape[1],
                                              repeatz=shape[2],
                                              base=int(base))
    return normalize_noise(noise_array)

# Создание квантовой пены
def create_foam(base, scale):
    noise_array = generate_noise(base, scale)
    U = np.where(noise_array > 0.5, noise_array, noise_array.min())
    U = normalize_noise(U)
    verts, faces, normals, values = measure.marching_cubes(U, level=0.5)
    return verts, faces

# Отрисовка квантовой пены
def draw_foam(verts, faces):
    glBegin(GL_TRIANGLES)
    for face in faces:
        for vert in face:
            glVertex3fv(verts[vert])
    glEnd()

# Основной цикл
base = 0
scale = 10
x_offset = 0
z_offset = 0
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
    glPushMatrix()
    glTranslatef(x_offset, 0, z_offset)
    base += 1
    verts, faces = create_foam(base, scale)
    draw_foam(verts, faces)
    glPopMatrix()
    pygame.display.flip()
    clock.tick(60)
