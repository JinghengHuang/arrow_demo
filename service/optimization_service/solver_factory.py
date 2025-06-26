from service.optimization_service.solver import BaseSolver
from service.optimization_service.pyomo.cobra_lp_solver import CobraLPSolver
from service.optimization_service.pyomo.glpk_solver_example import GlpkSolverSample

class SolverFactory:
    def __init__(self):
        self._solver_map = {
            "pyomo.glpk_solver_example": GlpkSolverSample(),
            "pyomo.cobra_lp": CobraLPSolver()
        }
        pass
        
    def get_solver(self, name:str) -> BaseSolver:
        return self._solver_map.get(name)