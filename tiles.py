#!/usr/bin/env python
import logging

from pyomo.environ import *
from twimage import get_cmap, RectObj, Point, RectDim, plot_rectangles, Rectangle

from BaseModel import BaseModel
import inventory
# from inventory import inv_5_5, inv_28_28, inv_10_10, inv_14_14, inv_18_18, inv_max
from visualize import Cover

_log = logging.getLogger(__name__)


class Tiles(BaseModel):

    def __init__(self, name: str, config: dict):
        super().__init__(name)

        self.config = config
        model = self.instance

        c = config.get('cover')

        self.R = c
        self.cover = c.cover
        self.inventory = c.inventory
        self.dimension = c.dimension
        self.tiles = c.tiles

        inventory = self.inventory
        cover = self.cover
        tiles = self.tiles

        ################################################################################
        # Sets
        ################################################################################

        model.I = RangeSet(self.dimension + 1)
        model.J = RangeSet(self.dimension + 1)
        model.K = RangeSet(len(self.tiles))

        ################################################################################
        # Params put at model
        ################################################################################

        model.cover = Param(model.K, model.I, model.J, model.I, model.J, initialize=cover)

        def size_init(model, k):
            return self.tiles[k] ** 2

        model.size = Param(model.K, initialize=size_init)

        ################################################################################
        # Var
        ################################################################################

        model.x = Var(model.K, model.I, model.J, domain=Boolean, initialize=0)

        model.y = Var(model.I, model.J, domain=Boolean, initialize=0)  # can be relaxed to [0,1]
        # model.y = Var(model.I, model.J, domain=NonNegativeReals, initialize=0)
        # model.y_relax_c = Constraint(model.I, model.J, rule=lambda model, i, j: 0 <= model.y[i, j] <= 1)

        model.delta = Var(model.I, domain=Boolean, initialize=0)
        model.w = Var(domain=NonNegativeReals, initialize=self.dimension, doc='max width of space we can fill')

        ################################################################################
        # Constraints
        ################################################################################

        model.tile_c = Constraint(
            model.K,
            rule=lambda model, k: sum(model.x[k, i, j] for i in model.I for j in model.J) <= 1
        )

        def all_covered_c(model, ii, jj):
            covers = [key for key, _ in cover.items() if (key[3] == ii and key[4] == jj)]
            return sum(model.cover[k, i, j, ii, jj] * model.x[k, i, j]
                       for (k, i, j, ii, jj) in covers) == model.y[ii, jj]

        model.all_covered_c = Constraint(model.I, model.J, rule=all_covered_c)

        def pattern_compact_c(model, i):
            if i == 1:
                return Constraint.Skip
            else:
                return model.delta[i] <= model.delta[i - 1]

        model.pattern_compact_c = Constraint(model.I, rule=pattern_compact_c)

        model.pattern_length_c = Constraint(rule=lambda mode: sum(model.delta[i] for i in model.I) == model.w)

        model.y_i_c = Constraint(model.I, model.J, rule=lambda model, i, j: model.y[i, j] <= model.delta[i])
        model.y_j_c = Constraint(model.I, model.J, rule=lambda model, i, j: model.y[i, j] <= model.delta[j])
        model.y_c = Constraint(model.I, model.J,
                               rule=lambda model, i, j: model.y[i, j] >= model.delta[i] + model.delta[j] - 1)

        ################################################################################
        # Objective
        ################################################################################
        def obj_profit(model):
            return model.w

        model.objective = Objective(rule=obj_profit, sense=maximize)

    def show(self):
        result = {k: v for (k, v) in self.result['x'].items() if v > 0}
        rects = list()

        rects.append(Rectangle(RectObj(Point(0,0), RectDim(self.dimension, self.dimension)), filled=False, color='grey'))
        for n, r in enumerate(result):
            print(r)
            k, i, j = r
            length = self.tiles[k]
            rects.append(Rectangle(RectObj(Point(i-1, j-1), RectDim(length, length)), text=f"{length}"))

        plot_rectangles(rects, autocolor=True, cmap_name='plasma')


if __name__ == "__main__":
    log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
    logging.basicConfig(format=log_fmt, level=logging.DEBUG)
    logging.getLogger('matplotlib').setLevel(logging.INFO)
    print(f"{'Tiles':.^80}")

    config = dict()

    # c = Cover(inventory=inv_5_5)
    # name = 'inv_10_10'
    # name = 'inv_14_14'
    # name = 'inv_18_18'
    # name = 'inv_28_28'
    # name = 'inv_5_5'
    name = 'inv_max2'
    c = Cover(inventory=getattr(inventory, name))

    c.create_cover()
    config['cover'] = c

    m = Tiles(name=name, config=config)
    m.save_model()
    m.solve(tee=False)
    m.save_result()
    m.show()
