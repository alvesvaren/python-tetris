import pyglet

from .tetris import blocks, Tetris

window = pyglet.window.Window()

print(blocks)

@window.event
def on_draw():
    window.clear()


pyglet.app.run()
