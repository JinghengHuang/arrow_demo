from .base_model import ArrowModel

"""
    class SolverConfig:
    This class is used to store the configuration for the solver.
    It includes the solver name, the solver type, and any additional parameters needed for the solver
"""

class SolverConfig(ArrowModel):
    def __init__(self, solver_name: str, solver_type: str, params: dict = None):
        """
        Initialize the SolverConfig with the solver name, type, and parameters.
        
        :param solver_name: Name of the solver (e.g., "Highs", "GLPK", etc.)
        :param solver_type: Type of the solver (e.g., "LP", "MILP", etc.)
        :param params: Additional parameters for the solver, if any
        """
        self.solver_name = solver_name
        if not solver_name:
            raise ValueError("Solver name cannot be empty.")
        self.solver_type = solver_type
        if solver_type is None or solver_type.upper() not in ["LP", "QP"]:
            raise ValueError(f"Unsupported solver type: {solver_type}. Supported types are: LP, QP.")
        self.params = params if params is not None else {}
        
    def sanity_check(self) -> None:
        return super().sanity_check()
    
    @classmethod
    def from_dict(cls, solver_dict: dict) -> "SolverConfig":
        """
        Create a SolverConfig instance from a dictionary representation.
        
        :param solver_dict: Dictionary containing solver configuration
        :return: SolverConfig instance
        """
        print("type of solver_dict: ", type(solver_dict))
        print("solver_dict: ", solver_dict)
        
        solver_name = solver_dict.get("solver_name")
        solver_type = solver_dict.get("solver_type")
        params = solver_dict.get("params", {})
        
        return cls(solver_name=solver_name, solver_type=solver_type, params=params)
        
    