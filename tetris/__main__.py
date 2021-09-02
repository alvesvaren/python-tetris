import pyglet
import pyglet.window.key as key
from . import BlockPart, State, div_vec

state = State()

block_size = 33
grid_color = 33, 33, 33
width, height = state.board.width, state.board.height

window = pyglet.window.Window(
    width=(width)*block_size, height=(height)*block_size)


def ltg(x: int, y: int):
    """Convert local coordinate to global coordinate (where on screen to render)"""
    return x * block_size, (height - y) * block_size


@window.event
def on_draw():
    window.clear()
    draw_grid()
    draw_ghost_block()
    draw_blocks()


def draw_grid():
    for y in range(height):
        x1, y1, x2, y2 = ltg(0, y + 1) + ltg(width + 1, y + 1)
        pyglet.shapes.Line(x1, y1, x2, y2, 1, grid_color).draw()
    for x in range(width):
        x1, y1, x2, y2 = ltg(x + 1, 0) + ltg(x + 1, height)
        pyglet.shapes.Line(x1, y1, x2, y2, 1, grid_color).draw()


def draw_blocks():
    block_parts: list[tuple[int, int, BlockPart]] = []
    for y, row in enumerate(state.board.board):
        for x, block_part in enumerate(row):
            if block_part:
                block_parts.append((x, y, block_part))
    for y, row in enumerate(state.current.matrix):
        for x, block_part in enumerate(row):
            if block_part:
                block_parts.append((x + state.x, y + state.y, block_part))
    for x, y, block_part in block_parts:
        args = *ltg(x, y), block_size, block_size
        pyglet.shapes.BorderedRectangle(
            *args, 4, block_part.color, div_vec(block_part.color, 2)).draw()

def draw_ghost_block():
    block_parts: list[tuple[int, int, BlockPart]] = []
    for y, row in enumerate(state.current.matrix):
        for x, block_part in enumerate(row):
            if block_part:
                block_parts.append((x + state.x, y + state.bottom_fitting_y, block_part))
    for x, y, block_part in block_parts:
        args = *ltg(x, y), block_size, block_size
        pyglet.shapes.BorderedRectangle(
            *args, 3, div_vec(block_part.color, 8), div_vec(block_part.color, 3)).draw()

@window.event
def on_key_press(symbol, modifiers):
    if symbol in [key.A, key.LEFT]:
        state.left()
    elif symbol in [key.D, key.RIGHT]:
        state.right()
    elif symbol in [key.S, key.DOWN]:
        state.soft_drop()
    elif symbol in [key.W, key.UP]:
        state.rotate()
    elif symbol == key.SPACE:
        state.hard_drop()
    elif symbol == key.C:
        state.stash()


def update(dt):
    state.tick()


pyglet.clock.schedule_interval(update, 1.5)

pyglet.app.run()
