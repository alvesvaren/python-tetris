from typing import Callable, Union
import pyglet
import pyglet.window.key as key
from . import BlockPart, State, div_vec

state = State()

block_size = 33
grid_color = 33, 33, 33
width, height = state.board.width, state.board.height

playfield_offset_x, playfield_offset_y = 200, 0

window = pyglet.window.Window(
    width=width*block_size + 400, height=height*block_size)


def ltg(x: int, y: int):
    """Convert local coordinate to global coordinate (where on screen to render)"""
    return x * block_size + playfield_offset_x, (height - (y + 1)) * block_size + playfield_offset_y


@window.event
def on_draw():
    window.clear()
    draw_playfield()


def draw_playfield():
    draw_grid()
    draw_ghost_block()
    draw_blocks()


def draw_block(x: int, y: int, color: Union[tuple[int, int, int], tuple[int, ...]], border_color: Union[tuple[int, int, int], tuple[int, ...]]):
    args = *ltg(x, y), block_size, block_size
    pyglet.shapes.BorderedRectangle(
        *args, 4, color, border_color).draw()


def draw_grid():
    for y in range(height - 1):
        x1, y1, x2, y2 = ltg(0, y) + ltg(width, y)
        pyglet.shapes.Line(x1, y1, x2, y2, 1, grid_color).draw()
    for x in range(width + 1):
        x1, y1, x2, y2 = ltg(x, -1) + ltg(x, height)
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
        draw_block(x, y, block_part.color, div_vec(block_part.color, 2))


def draw_ghost_block():
    block_parts: list[tuple[int, int, BlockPart]] = []
    for y, row in enumerate(state.current.matrix):
        for x, block_part in enumerate(row):
            if block_part:
                block_parts.append(
                    (x + state.x, y + state.bottom_fitting_y, block_part))
    for x, y, block_part in block_parts:
        draw_block(x, y, div_vec(block_part.color, 8), div_vec(block_part.color, 3))


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
    print(state.tick())


pyglet.clock.schedule_interval(update, 1.5)

pyglet.app.run()
