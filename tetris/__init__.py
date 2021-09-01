from random import shuffle
from typing import Optional, Union

shape = tuple[str, ...]

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
    new_shape = tuple("".join(row[::-1]) for row in zip(*shape))
    if offset == 1:
        return new_shape
    for _ in range(offset):
        return rotate(new_shape, offset - 1)
    return shape


class Block:
    def __init__(self, name: str, shape: shape, color: tuple[int, int, int]):
        self.name = name
        self.shape = shape
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
        print('\n'.join(self.matrix))


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
        self.board = [self.empty_row for y in range(self.height)]

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
        self.x, self.y = self.board.width//2 - 1, 0
        self.current, self.next = next(self.blocks), next(self.blocks)
        self.hold = None
        self.score = 0
        self.level = 1

    def tick(self):
        cleared_lines = self.board.clear_lines()
        assert cleared_lines <= 4
        self.score += scores_for_lines[cleared_lines] * (self.level + 1)

        self.current = self.next
        self.next = next(self.blocks)

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

    @property
    def ghost_y(self):
        dy = 0
        while self.board.fits_block(self.current, self.x, self.y + dy):
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
