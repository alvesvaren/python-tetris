import pyglet

from .tetris import blocks, Tetris

window = pyglet.window.Window()


@window.event
def on_draw():
    window.clear()


pyglet.app.run()
