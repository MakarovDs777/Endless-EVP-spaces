import noise
import pyglet
from pyglet.gl import *
from pyglet.window import key

# Класс для создания и управления 3D ландшафтом
class Terrain:
    def __init__(self, width, length, scale):
        self.width = width
        self.length = length
        self.scale = scale
        self.vertices = self.generate_vertices()

    def generate_vertices(self):
        vertices = []
        for z in range(self.length):
            for x in range(self.width):
                y = noise.pnoise2(x * self.scale, z * self.scale)
                vertices.extend([x, y, z])
        return ('v3f', vertices)

# Создание окна с помощью pyglet
window = pyglet.window.Window(resizable=True)

# Инициализация ландшафта
terrain = Terrain(width=100, length=100, scale=0.1)

# Функция для рендеринга сцены
@window.event
def on_draw():
    window.clear()
    glLoadIdentity()
    gluPerspective(35, window.width / window.height, 0.1, 1000.0)
    glTranslatef(-terrain.width//2, -5, -terrain.length)
    glRotatef(25, 1, 0, 0)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, terrain.vertices)
    glDrawArrays(GL_POINTS, 0, terrain.width * terrain.length)
    glDisableClientState(GL_VERTEX_ARRAY)

# Запуск приложения
pyglet.app.run()
