#!/usr/bin/env python
import logging
from pprint import pprint

from pyomo.environ import *
from twimage import Rectangle, RectObj, RectDim, Point, plot_rectangles

import settings
from BaseModel import BaseModel
from helper import Inventory

_log = logging.getLogger(__name__)


class Tiles(BaseModel):

    def __init__(self, name: str, config: dict) -> None:
        super().__init__(name)

        self.config = config
        self.inventory = config.get('inventory')
        self.dimension = self.inventory.dimension
        self.tiles = self.inventory.tiles
        self.n_tiles = len(self.tiles)

        model = self.instance  # from BaseModel

        ################################################################################
        # Sets
        ################################################################################

        model.I = RangeSet(self.n_tiles, doc='tile')
        model.J = Set(initialize=model.I)
        model.A = RangeSet(self.dimension, doc='max square area width')
        model.C = Set(initialize=['x', 'y'])
        model.K = Set(initialize=[True, False], doc='no overlap cases')

        ################################################################################
        # Params put at model
        ################################################################################

        M = self.dimension

        model.size = Param(model.I, initialize=self.tiles)
        model.size_space = Param(model.A, initialize=lambda model, a: a)  # TODO

        ################################################################################
        # Var
        ################################################################################

        model.t = Var(model.I, domain=Boolean, initialize=0, doc='selector for tile i')
        model.delta = Var(model.I, model.J, model.K, model.C, domain=Boolean, initialize=0)
        model.theta = Var(model.A, domain=Boolean, initialize=0, doc='selector for a')
        model.p = Var(model.I, model.C, domain=NonNegativeReals, initialize=0, doc='position per y,y')
        model.w = Var(domain=NonNegativeReals, initialize=self.dimension, doc='max width of space we can fill')
        model.a = Var(domain=NonNegativeReals, initialize=self.dimension, doc='max area of space we can fill')

        ################################################################################
        # Constraints
        ################################################################################

        model.inside_space_c = Constraint(
            model.I, model.C, rule=lambda model, i, c: model.p[i, c] + model.size[i] <= model.w
        )

        def no_overlap1_c(model, i, j, c):
            if i >= j:
                return Constraint.Skip
            return model.p[j, c] >= model.p[i, c] + model.size[i] - \
                   M * (1 - model.delta[i, j, True, c]) - \
                   M * (1 - model.t[i]) - \
                   M * (1 - model.t[j])

        model.no_overlap1_c = Constraint(
            model.I, model.J, model.C, rule=no_overlap1_c
        )

        def no_overlap2_c(model, i, j, c):
            if i >= j:
                return Constraint.Skip
            return model.p[j, c] + model.size[j] <= model.p[i, c] + \
                   M * (1 - model.delta[i, j, False, c]) + \
                   M * (1 - model.t[i]) + \
                   M * (1 - model.t[j])

        model.no_overlap2_c = Constraint(
            model.I, model.J, model.C, rule=no_overlap2_c
        )

        model.no_overlap_c = Constraint(
            model.I, model.J, rule=
            lambda model, i, j: sum(model.delta[i, j, k, c] for k in model.K for c in model.C) >= 1
        )

        model.width_c = Constraint(
            rule=lambda model: sum(model.size_space[a] * model.theta[a] for a in model.A) == model.w
        )
        model.area_c = Constraint(
            rule=lambda model: sum(model.size_space[a] ** 2 * model.theta[a] for a in model.A) == model.a
        )
        model.theta_c = Constraint(
            rule=lambda model: sum(model.theta[a] for a in model.A) == 1
        )

        model.total_area_c = Constraint(
            rule=lambda model: sum(model.size[i] ** 2 * model.t[i] for i in model.I) == model.a
        )

        # 28s 10_10: nice to have -> 14s
        def order1_c(model, i):
            if i == self.n_tiles:
                return Constraint.Skip
            if model.size[i] == model.size[i + 1]:
                return model.t[i] >= model.t[i + 1]
            return Constraint.Skip

        model.order1_c = Constraint(model.I, rule=order1_c)

        # 28s 10_10: nice to have2 -> 18/12s/9s/45s/2:22 -> without order1_c not solving
        def order2_c(model, i):
            if i == self.n_tiles:
                return Constraint.Skip
            if model.size[i] == model.size[i + 1]:
                return sum(model.p[i, c] for c in model.C) >= sum(model.p[i + 1, c] for c in model.C)
            return Constraint.Skip

        model.order2_c = Constraint(model.I, rule=order2_c)

        ################################################################################
        # Objective
        ################################################################################
        def obj_profit(model):
            return model.w

        model.objective = Objective(rule=obj_profit, sense=maximize)

    def show(self):
        if self.is_solved:
            # pprint(self.result)
            self.plot_squares()
        else:
            _log.info(f"Model not solved optimally.")

    def plot_squares(self):
        rects = list()
        for i in self.instance.I:
            length = self.tiles[i]
            if self.result['t'][i]:
                x = self.result['p'][i, 'x']
                y = self.result['p'][i, 'y']
                print(f"i:{i}, length: {length}, x:{x}, y:{y}")
                rects.append(
                    Rectangle(
                        RectObj(origin=Point(x, y), dimension=RectDim(length, length)),
                        text=f"{length}",
                        filled=True
                    )
                )
        plot_rectangles(rects, autocolor=True, cmap_name='plasma')


if __name__ == "__main__":
    log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
    logging.basicConfig(format=log_fmt, level=logging.DEBUG)
    logging.getLogger('matplotlib').setLevel(logging.INFO)
    print(f"{'Tiles':.^80}")

    # name = 'inv_5_5'
    # name = 'test'
    name = 'inv_10_10'
    inventory = Inventory(inventory=getattr(settings, name))
    config = dict(inventory=inventory)

    m = Tiles(name=name, config=config)
    m.save_model()
    m.solve(tee=False)
    m.save_model()
    m.save_result()
    m.show()
