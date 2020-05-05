import logging
import pytest

import settings
from helper import Inventory
from tiles import Tiles

log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
logging.basicConfig(format=log_fmt, level=logging.DEBUG)
logging.getLogger('matplotlib').setLevel(logging.INFO)

test1 = {
    1: 0,
    2: 4,
    # 3: 0,
}

inv_5_5 = {
    1: 4,
    2: 3,
    3: 2,
}


@pytest.mark.parametrize('config, is_solved', [
    (test1, True),
    (inv_5_5, True),
])
def test_model(config, is_solved):

    name = 'test'
    inventory = Inventory(inventory=config)
    config = dict(inventory=inventory)

    m = Tiles(name=name, config=config)
    # m.save_model()
    m.solve(tee=False)
    # m.save_model()
    # m.save_result()
    m.show()
    assert m.is_solved is is_solved
