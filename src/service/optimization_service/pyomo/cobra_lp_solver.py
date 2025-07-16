"""
This module implements a solver for linear programming problems using the Cobra LP solver.
"""
from service.optimization_service.pyomo.lp_problem import change_cobra_solver, LPProblem
from service.optimization_service.pyomo.solver import BaseSolver

class CobraLPSolver(BaseSolver):
    """Solver for linear programming problems using Cobra LP solver."""
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
        # Adapt to new solver names
        if model_conf.get("solver_name").lower() == "gurobi_persistent" or model_conf.get("solver_name").lower() == "gurobi":
            model_conf["solver_name"] = "gurobi_persistent_v2"
        if model_conf.get("solver_name").lower() == "gurobi_direct":
            model_conf["solver_name"] = "gurobi_direct_v2"
        
        solver_params = None
        if "solver_params" in model_conf:
            solver_params = model_conf["solver_params"]
        solver = change_cobra_solver(model_conf.get("solver_name") or "glpk")
        lp = LPProblem(self.model["A"], self.model["b"], self.model["c"], self.model["lb"], self.model["ub"], self.model["osense"], self.model["csense"])
        print("Building Model")
        try:
            lp.build_lp(solver)
            lp.solve(solver_params)
            return {
                "success": True,
                "solution": lp.solution,
                "status": lp.status,
                "obj_val": lp.objective_value
            }
        except Exception as e:
            return {
                "success": False,
                "error_message:": str(e)
            }
