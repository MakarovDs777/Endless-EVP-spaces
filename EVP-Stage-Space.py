import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# Инициализация Pygame
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

# Настройка перспективы
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
glTranslatef(0.0, -1.0, -5)

# Функция для создания холмов
def terrain():
    glBegin(GL_QUADS)
    for x in range(-10, 10):
        for z in range(-10, 10):
            glColor3fv((0, 0.5, 0))  # Зеленый цвет
            glVertex3fv((x, random.uniform(-0.1, 0.1), z))
            glVertex3fv((x+1, random.uniform(-0.1, 0.1), z))
            glVertex3fv((x+1, random.uniform(-0.1, 0.1), z+1))
            glVertex3fv((x, random.uniform(-0.1, 0.1), z+1))
    glEnd()

# Основной цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Управление камерой
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        glTranslatef(-0.1, 0, 0)
    if keys[pygame.K_RIGHT]:
        glTranslatef(0.1, 0, 0)
    if keys[pygame.K_UP]:
        glTranslatef(0, 0.1, 0)
    if keys[pygame.K_DOWN]:
        glTranslatef(0, -0.1, 0)

    # Отрисовка сцены
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    terrain()
    pygame.display.flip()
    pygame.time.wait(10)
