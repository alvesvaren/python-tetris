from typing import Callable, Type
import pyglet
import pyglet.window.key as key
from . import BlockPart, State, div_vec

state = State()

block_size = 33
grid_color = 33, 33, 33
width, height = state.board.width, state.board.height

window = pyglet.window.Window(
    width=width*block_size, height=height*block_size)


def ltg(x: int, y: int):
    """Convert local coordinate to global coordinate (where on screen to render)"""
    return x * block_size, (height - (y + 1)) * block_size


@window.event
def on_draw():
    window.clear()
    draw_playfield(0, 0)


def draw_playfield(offset_x, offset_y):
    def new_ltg(x: int, y: int):
        nx, ny = ltg(x, y)
        return nx + offset_x, ny - offset_y
    draw_grid(new_ltg)
    draw_ghost_block(new_ltg)
    draw_blocks(new_ltg)


def draw_grid(ltg: Callable[[int, int], tuple[int, int]] = ltg):
    for y in range(height - 1):
        x1, y1, x2, y2 = ltg(0, y) + ltg(width, y)
        pyglet.shapes.Line(x1, y1, x2, y2, 1, grid_color).draw()
    for x in range(width):
        x1, y1, x2, y2 = ltg(x, -1) + ltg(x, height)
        pyglet.shapes.Line(x1, y1, x2, y2, 1, grid_color).draw()


def draw_blocks(ltg: Callable[[int, int], tuple[int, int]] = ltg):
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


def draw_ghost_block(ltg: Callable[[int, int], tuple[int, int]] = ltg):
    block_parts: list[tuple[int, int, BlockPart]] = []
    for y, row in enumerate(state.current.matrix):
        for x, block_part in enumerate(row):
            if block_part:
                block_parts.append(
                    (x + state.x, y + state.bottom_fitting_y, block_part))
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
        state.finish_drop()
    elif symbol == key.C:
        state.stash()


def update(dt):
    state.tick()


pyglet.clock.schedule_interval(update, 1.5)

pyglet.app.run()
