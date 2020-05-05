import logging
import math
from typing import Dict

import settings

_log = logging.getLogger(__name__)


class Inventory(object):

    def __init__(self, inventory: Dict[int, int]) -> None:
        super().__init__()
        self.inventory = inventory
        self.max_tile_length = max(inventory.keys())

        self.tiles = self._create_tiles()

        self.total_area = sum(size ** 2 * count for size, count in self.inventory.items())
        self.dimension = int(math.sqrt(self.total_area))
        _log.info(f"Dim: {self.dimension}, longest tile: {self.max_tile_length}, total area: {self.total_area}")

    def _create_tiles(self):
        k = 1
        tiles = dict()
        for tile in self.inventory.keys():
            for i in range(self.inventory[tile]):
                tiles[k] = tile
                k += 1
        _log.info(f"{len(tiles)} tiles created.")
        return tiles


if __name__ == '__main__':
    log_fmt = r'%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s'
    logging.basicConfig(format=log_fmt, level=logging.DEBUG)
    logging.getLogger('matplotlib').setLevel(logging.INFO)

    name = 'inv_5_5'
    inventory = Inventory(inventory=getattr(settings, name))
