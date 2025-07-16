"""
This module implements a solver for quadratic programming problems using the Cobra QP solver.
"""
from service.optimization_service.pyomo.qp_problem import change_cobra_solver, QPProblem
from service.optimization_service.pyomo.solver import BaseSolver

class CobraQPSolver(BaseSolver):
    """Solver for quadratic programming problems using Cobra QP solver."""
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
        model_conf = self.model.get("solver")

        # Adapt to new solver names
        if model_conf.get("solver_name").lower() == "gurobi_persistent" or model_conf.get("solver_name").lower() == "gurobi":
            model_conf["solver_name"] = "gurobi_persistent_v2"
        if model_conf.get("solver_name").lower() == "gurobi_direct":
            model_conf["solver_name"] = "gurobi_direct_v2"

        solver_params = None
        if "solver_params" in model_conf:
            solver_params = model_conf["solver_params"]
        solver = change_cobra_solver(model_conf.get("solver_name") or "glpk")
        qp = QPProblem(self.model["A"], self.model["G"], self.model["Q"], self.model["b"], self.model["c"], self.model["h"], self.model["lb"], self.model["osense"], self.model["ub"])
        print("Building Model")
        try:
            qp.build_qp(solver)
            qp.solve(solver_params)
            return {
                "success": True,
                "solution": qp.solution,
                "status": qp.status,
                "obj_val": qp.objective_value
            }
        except Exception as e:
            return {
                "success": False,
                "error_message:": str(e)
            }
