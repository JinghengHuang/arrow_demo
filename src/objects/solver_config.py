from .base_model import ArrowModel

"""
    class SolverConfig:
    This class is used to store the configuration for the solver.
    It includes the solver name, the solver type, and any additional parameters needed for the solver
"""

class SolverConfig(ArrowModel):
    def __init__(self, solver_name: str, solver_type: str = "LP", params: dict = None):
        """
        Initialize the SolverConfig with the solver name, type, and parameters.
        
        :param solver_name: Name of the solver (e.g., "Highs", "GLPK", etc.)
        :param solver_type: Type of the solver (e.g., "LP", "MILP", etc.)
        :param params: Additional parameters for the solver, if any
        """
        self.solver_name = solver_name
        self.solver_type = solver_type
        if solver_type.upper() not in ["LP", "QP"]:
            raise ValueError(f"Unsupported solver type: {solver_type}. Supported types are: LP, QP.")
        print(f"solver parameters: {params}")
        print(f"type of params: {type(params)}")
        self.params = params if params is not None else {}
        
    def sanity_check(self) -> None:
        return super().sanity_check()
        
    