from random import shuffle
from typing import Optional, TypeVar

Shape = list[tuple[Optional['BlockPart'], ...]]

names = ("I", "J", "L", "O", "S", "T", "Z")
shapes = (
    ("....", "XXXX", "....", "...."),
    ("X..", "XXX", "...",),
    ("..X", "XXX", "..."), ("XX", "XX"),
    (".XX", "XX.", "..."), (".X.", "XXX", "..."),
    ("XX.", ".XX", "..."))
colors = (
    (0, 255, 255), (0, 0, 255), (255, 170, 0),
    (255, 255, 0), (0, 255, 0), (153, 0, 255), (255, 0, 0))


def div_vec(vec: tuple[int, ...], scalar: int):
    return *map(lambda x: x // scalar, vec),


def div_vec_f(vec: tuple[float, ...], scalar: float):
    return *map(lambda x: x / float(scalar), vec),


def rotate(shape: Shape, offset: int = 1) -> Shape:
    offset %= 4
    new_shape = [row[::-1] for row in zip(*shape)]
    if offset == 1:
        return new_shape
    for _ in range(offset):
        return rotate(new_shape, offset - 1)
    return shape


class BlockPart:
    def __init__(self, color: tuple[int, int, int]):
        self.color = color


class Block:
    def __init__(self, name: str, raw_shape: tuple[str, ...], color: tuple[int, int, int]):
        self.name = name
        self.shape: Shape = [tuple(BlockPart(
            color) if char == "X" else None for char in row) for row in raw_shape]
        self.rotation = 0
        self.color = color

    def rotate(self, offset: int = 1):
        self.rotation += offset
        return self

    def __repr__(self):
        return f"Block({self.name}, rot={self.rotation})"

    @property
    def matrix(self):
        return rotate(self.shape, self.rotation)

    @property
    def height(self):
        height = len(self.matrix) - 1
        for row in self.matrix[::-1]:
            if any(row):
                break
            else:
                height -= 1
        return height

    def pprint_matrix(self):
        print(str(self))

    @property
    def max_x(self):
        cols = tuple(zip(*self.matrix))[::-1]
        min_x = len(cols)
        for col in cols:
            if any(col):
                break
            else:
                min_x -= 1
        return min_x

    @property
    def min_x(self):
        min_x = 0
        for col in tuple(zip(*self.matrix)):
            if any(col):
                break
            else:
                min_x += 1
        return min_x

    def __str__(self):
        return '\n'.join(map(lambda x: ''.join(map(lambda x: "X" if x else ".", x)), self.matrix))


blocks = [Block(*block) for block in zip(names, shapes, colors)]


def _generate_bag():
    bag = blocks.copy()
    shuffle(bag)

    while bag:
        yield bag[0]
        bag.pop(0)


def generate_blocks():
    while True:
        yield from _generate_bag()


class BaseBoard:
    width, height = 10, 20
    empty_row: list[Optional[BlockPart]] = [None for _ in range(width)]

    def __init__(self):
        self.board = [
            self.empty_row.copy() for _ in range(self.height)]

    def __getitem__(self, *args, **kwargs):
        return self.board.__getitem__(*args, **kwargs)

    def intersect(self, other: 'BaseBoard'):
        return [[self[y][x] or other[y][x] for x in range(self.width)] for y in range(self.height)]

    def fits_block(self, block: Block, dx: int, dy: int):
        for y, row in enumerate(block.matrix):
            for x, part in enumerate(row):
                if not part:
                    continue
                try:
                    if self[y + dy][x + dx]:
                        return False
                except IndexError:
                    return False
        return True

    def place_block(self, block: Block, dx: int, dy: int):
        if not self.fits_block(block, dx, dy):
            raise ValueError(f"Block does not fit at: x={dx} y={dy}")
        for y, row in enumerate(block.matrix):
            for x, part in enumerate(row):
                if part:
                    self.board[y + dy][x + dx] = part


class GameBoard(BaseBoard):
    def clear_lines(self):
        lines_cleared = 0
        for y, row in enumerate(self.board):
            if all(row):
                lines_cleared += 1
                self.board.pop(y)
                self.board.insert(0, self.empty_row.copy())
        return lines_cleared


scores_for_lines = (0, 100, 300, 500, 800)
gravity_for_level = div_vec_f((48, 43, 38, 33, 28, 23, 18, 13, 8, 6,
                               5, 5, 5, 4, 4, 4, 3, 3, 3) + ((2,) * 10), 30)


class State:
    def __init__(self):
        self.blocks = generate_blocks()
        self.board = GameBoard()
        self.default_x = self.board.width//2 - 1
        self.x, self.y = self.default_x, 0
        self.current, self.next = next(self.blocks), next(self.blocks)
        self.hold = None
        self.cleared_lines = 0
        self.score = 0
        self.did_stash = False

    def tick(self):
        self.soft_drop()
        if self.y >= (self.bottom_fitting_y):
            self.finish_drop()

        return self.gravity

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

    @property
    def gravity(self):
        if self.level < len(gravity_for_level):
            return gravity_for_level[self.level]
        return 1

    @property
    def level(self):
        return self.cleared_lines//10

    @property
    def bottom_fitting_y(self):
        dy = self.y
        while self.board.fits_block(self.current, self.x, dy):
            dy += 1
        return dy - 1

    @property
    def fits(self):
        return self.board.fits_block(self.current, self.x, self.y)

    def soft_drop(self):
        self.y += 1

    def left(self):
        self.x -= 1
        if not self.fits:
            self.x += 1
        self.constrain()

    def right(self):
        self.x += 1
        if not self.fits:
            self.x -= 1
        self.constrain()

    def rotate(self, offset: int = 1):
        self.current.rotate(offset)
        self.constrain()
        if not self.fits:
            self.x += 1
            if not self.fits:
                self.x -= 2
                if not self.fits:
                    self.current.rotate(-offset)

    def constrain(self):
        while self.x + self.current.max_x > self.board.width:
            self.x -= 1

        while self.x + self.current.min_x < 0:
            self.x += 1

    def stash(self):
        if not self.did_stash:
            had_stashed = self.hold
            self.hold = self.current
            if had_stashed:
                self.current = had_stashed
            else:
                self.current = self.next
                self.next = next(self.blocks)

            self.x, self.y = self.default_x, 0
            self.did_stash = True

    def finish_drop(self):
        self.board.place_block(self.current, self.x, self.bottom_fitting_y)
        self.current = self.next
        self.next = next(self.blocks)
        self.x, self.y = self.default_x, 0
        self.did_stash = False

        cleared_lines = self.board.clear_lines()
        self.score += scores_for_lines[cleared_lines] * (self.level + 1)
