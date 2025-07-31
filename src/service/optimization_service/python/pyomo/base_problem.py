from utils.pyomo_utils import *

class BaseProblem():
    """Base class for pyomo optimization problems
    """
    def __init__(self):
        pass
    def build(self, solver: SolverConfig):
        pass
    def solve(self, solver_params=None):
        pass