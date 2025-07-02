
import pyomo.environ as pyo
import pyarrow as pa
import numpy as np
from service.optimization_service.pyomo.cobra_lp import change_cobra_solver, LPProblem
from service.optimization_service.solver import BaseSolver

class CobraLPSolver(BaseSolver):
    def __init__(self):
        self.model = {}
        super().__init__()
        
        
    def run(self, params:dict) -> dict:
        # Convert the data into an model acceptable format
        for k, v in params.items():
            self.model[k] = v
        
        # Send the data to model
        # Get results, for now just use glpk
        solver = change_cobra_solver("glpk")
        lp = LPProblem(self.model["S"], self.model["b"], self.model["c"], self.model["lb"], self.model["ub"], self.model["osense"], self.model["csense"])
        lp.build_lp(solver)
        lp.solve()
        return {
            "solution": lp.solution,
            "status": lp.status,
            "obj_val": lp.objective_value
        }
