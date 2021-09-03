from typing import Callable, Generator, Iterable, TypeVar, Union
import pyglet
import pyglet.window.key as key
from . import BlockPart, State, div_vec, Block

state = State()

block_size = 33
small_block_size = block_size // 2
grid_color = 33, 33, 33
width, height = state.board.width, state.board.height
playfield_offset_x, playfield_offset_y = 200, 0
font = "Open Sans"

window = pyglet.window.Window(
    width=width*block_size + 400, height=height*block_size, caption="Tetris")

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
    draw_block_container(block_size, block_size *
                         (height - 4), state.hold, "HOLD")
    draw_block_container(block_size * (width + 1) +
                         playfield_offset_x, block_size * (height - 4), state.next, "NEXT")

    pyglet.text.Label(f"Level: {state.level}", font,
                      20, True, x=block_size, y=block_size).draw()
    pyglet.text.Label(f"Score: {state.score}", font,
                      20, True, x=block_size, y=block_size * 2).draw()


def draw_block_container(dx: int, dy: int, block: Union[Block, None], text: str):
    container_width = small_block_size * 6
    pyglet.shapes.BorderedRectangle(
        dx, dy,
        container_width, small_block_size * 4, 16, (50, 50, 50), (33, 33, 33)).draw()
    pyglet.text.Label(text, font, 20, True, color=(
        255, 255, 255, 255), x=dx + container_width // 2, y=dy + small_block_size * 5, anchor_x='center').draw()
    if block:
        for x, y, block_part in generate_matrix(block.slim_shape[::-1]):
            if block_part:
                local_x, local_y = (x - 1) * small_block_size + dx + \
                    small_block_size * 2, y * small_block_size + dy + small_block_size
                pyglet.shapes.BorderedRectangle(
                    local_x, local_y, small_block_size, small_block_size, 2, block_part.color, div_vec(block_part.color, 2)).draw()


def intermediate_left(dt):
    if keys[key.A] or keys[key.LEFT]:
        pyglet.clock.schedule_interval(repeat_left, 1/20)


def intermediate_right(dt):
    if keys[key.D] or keys[key.RIGHT]:
        pyglet.clock.schedule_interval(repeat_right, 1/20)


@window.event
def on_key_press(symbol: int, modifiers: int):
    if symbol in [key.A, key.LEFT]:
        state.left()
        pyglet.clock.schedule_once(intermediate_left, 1/3)
    elif symbol in [key.D, key.RIGHT]:
        state.right()
        pyglet.clock.schedule_once(intermediate_right, 1/3)
    elif symbol in [key.S, key.DOWN]:
        pyglet.clock.unschedule(update)
        update(None)
    elif symbol in [key.W, key.UP]:
        holding_shift = bool(modifiers & key.MOD_SHIFT)
        state.rotate(-1 if holding_shift else 1)
    elif symbol == key.SPACE:
        state.finish_drop()
    elif symbol == key.C:
        state.stash()


@window.event
def on_key_release(symbol, modifiers):
    if symbol in [key.A, key.LEFT]:
        pyglet.clock.unschedule(repeat_left)
        pyglet.clock.unschedule(intermediate_left)
    elif symbol in [key.D, key.RIGHT]:
        pyglet.clock.unschedule(repeat_right)
        pyglet.clock.unschedule(intermediate_right)
    elif symbol in [key.S, key.DOWN]:
        pyglet.clock.unschedule(update)


keys = key.KeyStateHandler()
window.push_handlers(keys)


def schedule_func(func: Callable):

    pyglet.clock.schedule_once(lambda _: pyglet.clock.schedule_interval(
        func, 1/20) if keys[key.A] or keys[key.LEFT] else None, 1/2)


def repeat_left(dt):
    if keys[key.A] or keys[key.LEFT]:
        state.left()


def repeat_right(dt):
    if keys[key.D] or keys[key.RIGHT]:
        state.right()


def update(dt: Union[float, None]):
    next_tick = state.tick(keys[key.S] or keys[key.DOWN])
    pyglet.clock.schedule_once(update, next_tick)


update(None)

pyglet.app.run()
