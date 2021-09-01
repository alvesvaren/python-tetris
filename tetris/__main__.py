from typing import Type
import pyglet
import pyglet.window.key as key
from . import Block, BlockPart, State

window = pyglet.window.Window()

state = State()

block_size = 25


@window.event
def on_draw():
    window.clear()
    draw_static_blocks()
    draw_current_block()


def draw_static_blocks():
    blocks: list[tuple[int, int, Block]] = []
    for y, row in enumerate(state.board.board):
        for x, block in enumerate(row):
            if block:
                blocks.append((x, y, block))
    for x, y, block in blocks:
        pyglet.shapes.Rectangle(
            x * block_size, y * block_size, block_size, block_size, block.color).draw()


def draw_current_block():
    blocks: list[tuple[int, int, BlockPart]] = []
    for y, row in enumerate(state.current.matrix):
        for x, block_part in enumerate(row):
            if block_part.active:
                blocks.append((x, y, block_part))
    for x, y, block_part in blocks:
        pyglet.shapes.Rectangle(
            x * block_size, y * block_size, block_size, block_size, block_part.color).draw()


@window.event
def on_key_press(symbol, modifiers):
    if symbol in [key.A, key.LEFT]:
        state.left()
    elif symbol in [key.D, key.RIGHT]:
        state.right()
    elif symbol in [key.S, key.DOWN]:
        state.soft_drop()
    elif symbol in [key.W, key.UP]:
        state.current.rotate().pprint_matrix()
    elif symbol == key.SPACE:
        state.hard_drop()
    elif symbol == key.C:
        state.stash()


def update(dt):
    state.tick()


pyglet.clock.schedule_interval(update, 1)

pyglet.app.run()
