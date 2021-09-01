import pyglet

from .tetris import blocks, generate_blocks

window = pyglet.window.Window()
blocks = generate_blocks()
for _ in range(20):
    print(next(blocks))

@window.event
def on_draw():
    window.clear()


pyglet.app.run()
