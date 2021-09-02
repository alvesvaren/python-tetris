from random import shuffle
from typing import Optional, Type, Union

shape = list[tuple['BlockPart', ...]]

names = (
    "I",
    "J",
    "L",
    "O",
    "S",
    "T",
    "Z")
shapes = ((
    "....",
    "XXXX",
    "....",
    "...."), (
    "X..",
    "XXX",
    "...",), (
    "..X",
    "XXX",
    "..."), (
    "XX",
    "XX"), (
    ".XX",
    "XX.",
    "..."), (
    ".X.",
    "XXX",
    "..."), (
    "XX.",
    ".XX",
    "..."))
colors = (
    (0, 255, 255),
    (0, 0, 255),
    (255, 170, 0),
    (255, 255, 0),
    (0, 255, 0),
    (153, 0, 255),
    (255, 0, 0))


def rotate(shape: shape, offset: int = 1) -> shape:
    offset %= 4
    new_shape = [row[::-1] for row in zip(*shape)]
    if offset == 1:
        return new_shape
    for _ in range(offset):
        return rotate(new_shape, offset - 1)
    return shape


class BlockPart:
    def __init__(self, color: tuple[int, int, int], active: bool):
        self.color = color
        self.active = active

    def __repr__(self):
        return 'X' if self.active else "."


class Block:
    def __init__(self, name: str, raw_shape: tuple[str, ...], color: tuple[int, int, int]):
        self.name = name
        self.shape = [tuple(BlockPart(color, char == "X")
                            for char in row) for row in raw_shape]
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

    def pprint_matrix(self):
        print(str(self))

    def __str__(self):
        return '\n'.join(map(lambda x: ''.join(map(repr, x)), self.matrix))


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
    empty_row = [None for _ in range(width)]

    def __init__(self):
        self.board: list[Union[list[None], list[Block]]] = [
            self.empty_row for y in range(self.height)]

    def __getitem__(self, *args, **kwargs):
        return self.board.__getitem__(*args, **kwargs)

    def intersect(self, other: 'BaseBoard'):
        return [[self[y][x] or other[y][x] for x in range(self.width)] for y in range(self.height)]

    def fits_block(self, block: Block, dx: int, dy: int):
        for y, row in enumerate(block.matrix):
            for x, char in enumerate(row):
                if char == "X" and self[y + dy][x + dx]:
                    return False
        return True


class GameBoard(BaseBoard):
    def clear_lines(self):
        lines_cleared = 0
        for y, row in enumerate(self.board):
            if all(row):
                lines_cleared += 1
                self.board.pop(y)
                self.board.insert(0, self.empty_row)
        return lines_cleared


scores_for_lines = [0, 40, 100, 300, 1200]


class State:
    def __init__(self):
        self.blocks = generate_blocks()
        self.board = GameBoard()
        # self.player_board = BaseBoard()
        self.default_x = self.board.width//2 - 1
        self.x, self.y = self.default_x, 0
        self.current, self.next = next(self.blocks), next(self.blocks)
        self.hold = None
        self.score = 0
        self.level = 1
        self.did_stash = False

    def tick(self):
        cleared_lines = self.board.clear_lines()
        assert cleared_lines <= 4
        self.score += scores_for_lines[cleared_lines] * (self.level + 1)
        self.soft_drop()

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

    @property
    def ghost_y(self):
        dy = 0
        while self.board.fits_block(self.current, self.x, self.y + dy):
            if (dy < 0 or dy > self.board.height):
                break
            dy += 1
        return self.y + dy

    def hard_drop(self):
        self.y += self.ghost_y

    def soft_drop(self):
        self.y += 1

    def left(self):
        self.x -= 1

    def right(self):
        self.x += 1

    def stash(self):
        self.hold = self.current
        self.current = self.next
        self.x, self.y = self.default_x, 0
        self.did_stash = True

    def _finish_drop(self):
        self.current = self.next
        self.next = next(self.blocks)
        self.x, self.y = self.default_x, 0
        self.did_stash = False
