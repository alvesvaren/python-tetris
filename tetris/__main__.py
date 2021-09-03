from typing import Generator, Iterable, TypeVar, Union
import pyglet
import pyglet.window.key as key
from . import BlockPart, State, div_vec

state = State()

block_size = 33
small_block_size = block_size // 2
grid_color = 33, 33, 33
width, height = state.board.width, state.board.height
playfield_offset_x, playfield_offset_y = 200, 0

window = pyglet.window.Window(
    width=width*block_size + 400, height=height*block_size)

T = TypeVar("T")


def ltg(x: int, y: int):
    """Convert local coordinate to global coordinate (where on screen to render)"""
    return x * block_size + playfield_offset_x, (height - (y + 1)) * block_size + playfield_offset_y


@window.event
def on_draw():
    window.clear()
    draw_playfield()


def draw_playfield():
    draw_grid()
    draw_ghost_blocks()
    draw_blocks()
    draw_ui()


def generate_matrix(matrix: Iterable[Iterable[T]]) -> Generator[tuple[int, int, T], None, None]:
    for y, row in enumerate(matrix):
        for x, val in enumerate(row):
            yield x, y, val


def draw_block(x: int, y: int, color: Union[tuple[int, int, int], tuple[int, ...]], border_color: Union[tuple[int, int, int], tuple[int, ...]]):
    pyglet.shapes.BorderedRectangle(
        *ltg(x, y), block_size, block_size, 4, color, border_color).draw()


def draw_grid():
    for y in range(height - 1):
        x1, y1, x2, y2 = ltg(0, y) + ltg(width, y)
        pyglet.shapes.Line(x1, y1, x2, y2, 1, grid_color).draw()
    for x in range(width + 1):
        x1, y1, x2, y2 = ltg(x, -1) + ltg(x, height)
        pyglet.shapes.Line(x1, y1, x2, y2, 1, grid_color).draw()


def draw_ghost_blocks():
    for x, y, block_part in generate_matrix(state.current.matrix):
        if block_part:
            draw_block(
                x + state.x, y + state.bottom_fitting_y, div_vec(block_part.color, 8), div_vec(block_part.color, 3))


def draw_blocks():
    def draw(x: int, y: int, part: BlockPart):
        draw_block(x, y, part.color, div_vec(part.color, 2))

    for x, y, block_part in generate_matrix(state.board.board):
        if block_part:
            draw(x, y, block_part)
    for x, y, block_part in generate_matrix(state.current.matrix):
        if block_part:
            draw(x + state.x, y + state.y, block_part)


def draw_ui():
    pyglet.text.Label("HOLD", "Open Sans", 24, True, color=(
        255, 255, 255, 255), x=block_size + (small_block_size * 8) // 2, y=block_size * (height - 1.2), anchor_x='center').draw()
    pyglet.shapes.BorderedRectangle(
        block_size, block_size * (height - 4),
        small_block_size * 8, small_block_size * 5, 16, (50, 50, 50), (33, 33, 33)).draw()
    draw_hold_block()


def draw_hold_block():
    if state.hold:
        for x, y, block_part in generate_matrix(state.hold.shape[::-1]):
            if block_part:
                local_x, local_y = x * small_block_size + block_size + \
                    small_block_size * 2, y * small_block_size + \
                    block_size * (height - 4)
                pyglet.shapes.BorderedRectangle(
                    local_x, local_y, small_block_size, small_block_size, 2, block_part.color, div_vec(block_part.color, 2)).draw()


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
