import logging
import time
from pprint import pprint

import dill
from pyomo.core import value, Var, Any, ConcreteModel
from pyomo.opt import SolverStatus, TerminationCondition, SolverFactory

_log = logging.getLogger(__name__)


class BaseModel(object):
    # opt = SolverFactory("glpk")
    opt = SolverFactory("cbc")
    opt.options["threads"] = 6

    def __init__(self, name: str) -> None:

        model = ConcreteModel()

        self.name = name
        self.is_solved = False
        self.objective = None
        self.instance = model
        self.result = dict()

    def save_model(self):
        self.instance.display(filename=f"{self.name}.display.dump")
        path = f"{self.name}.model.dump"
        with open(path, 'w') as output_file:
            self.instance.pprint(output_file)

    def solve(self, *args, **kwargs):
        start_time = time.time()

        result = self.opt.solve(self.instance)
        self.objective = value(self.instance.objective)

        # self.instance.display()
        self.show_result(result)

        # load the results
        for var in self.instance.component_objects(Var, active=True):
            _log.info(f"{var.name}: index dim: {var.dim()}, len: {len(var)}")
            self.result[var.name] = {k: v for (k, v) in self.instance.x.get_values().items()}

        self.instance.compute_statistics()
        _log.info(f"Number of constraints : {self.instance.statistics.number_of_constraints}")
        _log.info(f"Number of variables : {self.instance.statistics.number_of_variables}")

        elapsed_time = time.time() - start_time
        _log.info(f'Duration: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))}')

    def save_result(self):
        p = f"{self.name}.dill"
        _log.info(f"Saving result to: {p}.")
        with open(p, 'wb') as handle:
            dill.dump(self, handle)

    @staticmethod
    def load_result(p: str = 'result.dill') -> Any:
        """Loads full class via dill
        Tiles.load_result()
        """
        _log.info(f"Loading result from: {p}.")
        with open(p, 'rb') as handle:
            return dill.load(handle)

    def show_result(self, result):
        if (result.solver.status == SolverStatus.ok) and (
                result.solver.termination_condition == TerminationCondition.optimal
        ):
            _log.info("# feasible and optimal solution found")
            self.is_solved = True
            _log.info("# Solution {}".format(
                [result.Problem.get("Lower bound").value, result.Problem.get("Upper bound").value, ]
            ))
        elif result.solver.termination_condition == TerminationCondition.infeasible:
            _log.info("# no feasible solution found")
        else:
            _log.warning(str(result.solver))

    def show(self):
        raise NotImplementedError()
