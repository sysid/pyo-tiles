#!/usr/bin/env python
import logging
from pprint import pprint

from pyomo.environ import *

import settings
from BaseModel import BaseModel

_log = logging.getLogger(__name__)


class Template(BaseModel):

    def __init__(self, name: str, config: dict) -> None:
        super().__init__(name)

        self.config = config
        model = self.instance  # from BaseModel

        ################################################################################
        # Sets
        ################################################################################

        ################################################################################
        # Params put at model
        ################################################################################

        ################################################################################
        # Var
        ################################################################################

        ################################################################################
        # Constraints
        ################################################################################

        ################################################################################
        # Objective
        ################################################################################
        def obj_profit(model):
            cost = 0
            profit = 0
            return profit - cost

        model.objective = Objective(rule=obj_profit, sense=maximize)

    def show(self):
        pprint(self.result)


if __name__ == "__main__":
    log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
    logging.basicConfig(format=log_fmt, level=logging.DEBUG)
    logging.getLogger('matplotlib').setLevel(logging.INFO)
    print(f"{'Template':.^80}")

    name = 'inv_5_5'
    config = dict(inventory=getattr(settings, name))

    m = Template(name=name, config=config)
    m.save_model()
    m.solve(tee=False)
    m.save_model()
    m.save_result()
    m.show()
