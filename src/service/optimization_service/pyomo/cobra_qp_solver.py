
import pyomo.environ as pyo
import pyarrow as pa
import numpy as np
from service.optimization_service.pyomo.qp_problem import change_cobra_solver, QPProblem
from service.optimization_service.solver import BaseSolver

class CobraQPSolver(BaseSolver):
    def __init__(self):
        self.model = {}
        super().__init__()
        
        
    def run(self, params:dict) -> dict:
        # Convert the data into an model acceptable format
        for k, v in params.items():
            self.model[k] = v
        print("Solver start")
        # Send the data to model
        # Get results, using custom solver
        # Use compatible version of highs when using highs
        model_conf = self.model.get("solver")
        if model_conf.get("solver_name").upper() == "HIGHS":
            model_conf["solver_name"] = "appsi_highs"
        solver = change_cobra_solver(model_conf.get("solver_name") or "glpk")
        qp = QPProblem(self.model["A"], self.model["G"], self.model["Q"], self.model["b"], self.model["c"], self.model["h"], self.model["lb"], self.model["osense"], self.model["ub"])
        print("Building Model")
        # try:
        qp.build_qp(solver)
        qp.solve()
        return {
            "solution": qp.solution,
            "status": qp.status,
            "obj_val": qp.objective_value
        }
        # except Exception as e:
        #     return {
        #         "Exception:": str(e)
        #     }
