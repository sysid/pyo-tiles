import logging
import math
from collections import defaultdict, namedtuple
from itertools import combinations_with_replacement, product
import random
from typing import Tuple, List, Dict, Union

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle as mRectangle
from twimage import plot_rectangles

_log = logging.getLogger(__name__)

RectDim = namedtuple('RectDim', ['x', 'y'])
Point = namedtuple('Point', ['x', 'y'])
RectObj = namedtuple('RectObj', ['origin', 'dimension'])


class Cover(object):
    """Docstring for Cover. """

    def __init__(self, inventory: Dict[int, int]) -> None:
        super().__init__()
        self.inventory = inventory
        self.max_length = max(inventory.keys())

        area = sum(size ** 2 * count for size, count in self.inventory.items())
        self.dimension = int(math.sqrt(area))
        _log.info(f"Dim: {self.dimension}, longest tile: {self.max_length}")
        self.area = product(range(1, self.dimension + 1 + 1), repeat=2)

        self.tiles = self._create_tiles()
        self.cover = defaultdict(lambda: 0)

    def _create_tiles(self):
        k = 1
        tiles = dict()
        for tile in self.inventory.keys():
            for i in range(self.inventory[tile]):
                tiles[k] = tile
                k += 1
        _log.info(f"{len(tiles)} tiles created.")
        return tiles

    def _create_cover(self, t: Tuple[int, int, int]) -> Dict[Tuple[int, int, int, int, int], int]:
        k, i, j = t
        for ii in range(self.tiles[k]):
            for jj in range(self.tiles[k]):
                self.cover[(k, i, j, ii + i, jj + j)] = 1
        return self.cover

    def create_cover(self):
        for k, length in self.tiles.items():
            _log.info(f"Calc cover for tile {k}")
            for i in range(1, self.dimension + 2 - length):
                for j in range(1, self.dimension + 2 - length):
                    self._create_cover((k, i, j))


if __name__ == '__main__':
    log_fmt = r'%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s'
    logging.basicConfig(format=log_fmt, level=logging.DEBUG)
    logging.getLogger('matplotlib').setLevel(logging.INFO)

    inventory = {
        1: 6,
        2: 5,
        3: 4,
        4: 3,
        5: 2,
        6: 1,
    }

    r = Cover(inventory=inventory)
