from random import shuffle


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
    ".XX.",
    ".XX.",
    "...."), (
    ".XX",
    "XX.",
    "..."), (
    ".X.",
    "XXX",
    "..."), (
    "XX.",
    ".XX",
    "..."))
center_points = (
    (1.5, 1.5),
    (1, 1),
    (1, 1),
    (1.5, 1.5),
    (1, 1),
    (1, 1))
colors = (
    (0, 255, 255),
    (0, 0, 255),
    (255, 170, 0),
    (255, 255, 0),
    (0, 255, 0),
    (153, 0, 255),
    (255, 0, 0))


class Block:
    def __init__(self, shape: tuple[str, ...], center: tuple[float, float], color: tuple[int, int, int]):
        self.shape = shape
        self.center = center
        self.rotation = 0

    def rotate(self, offset: int):
        self.rotation += offset

    @property
    def matrix(self):
        return


blocks = [Block(*block) for block in zip(shapes, center_points, colors)]


class Tetris:
    def _generate_bag(self):
        bag = blocks.copy()
        shuffle(bag)

        while bag:
            yield bag[0]
            bag.pop(0)

    def generate_blocks(self):
        while True:
            yield from self._generate_bag()
