from service.optimization_service.python.pyomo.solver import BaseSolver
from service.optimization_service.python.pyomo.cobra_lp_solver import CobraLPSolver
from service.optimization_service.python.pyomo.cobra_qp_solver import CobraQPSolver

class SolverFactory:
    def __init__(self):
        self._solver_map = {
            "pyomo.lp": CobraLPSolver(),
            "pyomo.qp": CobraQPSolver()
        }
        pass

    def get_solver(self, name:str) -> BaseSolver:
        """Get a certain type of solver

        Args:
            name (str): _description_

        Returns:
            BaseSolver: _description_
        """
        return self._solver_map.get(name)
