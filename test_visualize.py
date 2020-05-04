import logging

import pytest
from twimage import RectObj, Point, RectDim

from visualize import Cover

_log = logging.getLogger(__name__)
log_fmt = r'%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s'
logging.basicConfig(format=log_fmt, level=logging.DEBUG)
logging.getLogger('matplotlib').setLevel(logging.INFO)


class TestCover:
    inventory = {
        1: 6,
        2: 5,
        3: 4,
        4: 3,
    }

    def test_init(self):
        cover = Cover(inventory=self.inventory)
        assert cover.dimension == 10

        # ok area has got one addition row/col
        assert len(list(cover.area)) == 11 ** 2

    @pytest.mark.parametrize('input, output', [
        (
                (5, 1, 5), (5, 1, 5, 1, 5)
        ),
    ])
    def test__create_cover(self, input, output):
        c = Cover(inventory=self.inventory)
        c._create_cover(input)
        tile = (5, 1, 5)
        k, i, j = tile
        assert c.cover[(k, i, j, 1, 5)] == 1
        assert c.cover[(k, i, j, 6, 9)] == 0

        # ro = RectObj(Point(i, j), RectDim(k, k))
        # c.plot_on_grid(ro)

    def test_create_cover(self):
        c = Cover(inventory=self.inventory)
        c.create_cover()
        assert len(c.cover) == 6876
