from service.optimization_service.solver import BaseSolver
from service.optimization_service.pyomo.cobra_lp_solver import CobraLPSolver
from service.optimization_service.pyomo.cobra_qp_solver import CobraQPSolver

class SolverFactory:
    def __init__(self):
        self._solver_map = {
            "pyomo.lp": CobraLPSolver(),
            "pyomo.qp": CobraQPSolver()
        }
        pass
        
    def get_solver(self, name:str) -> BaseSolver:
        return self._solver_map.get(name)