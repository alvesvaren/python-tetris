from random import shuffle

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
