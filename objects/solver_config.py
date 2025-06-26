"""
    class SolverConfig:
    This class is used to store the configuration for the solver.
    It includes the solver name, the solver type, and any additional parameters needed for the solver
"""



class SolverConfig:
    def __init__(self, solver_name: str, solver_type: str = "LP", params: dict = None):
        """
        Initialize the SolverConfig with the solver name, type, and parameters.
        
        :param solver_name: Name of the solver (e.g., "Highs", "GLPK", etc.)
        :param solver_type: Type of the solver (e.g., "LP", "MILP", etc.)
        :param params: Additional parameters for the solver, if any
        """
        self.solver_name = solver_name
        self.solver_type = solver_type
        if solver_type not in ["LP"]:
            raise ValueError(f"Unsupported solver type: {solver_type}. Supported types are: LP.")
        print(f"solver parameters: {params}")
        print(f"type of params: {type(params)}")
        self.params = params if params is not None else {}
        
    def to_pydict(self):
        """
        Convert the SolverConfig to a dictionary for serialization.
        
        :return: A dictionary representation of the SolverConfig
        """
        solver_dict = {
            "solver_name": self.solver_name,
            "solver_type": self.solver_type,
        }
        if self.params:
            for key, value in self.params.items():
                solver_dict[key] = value
        return {"solver":solver_dict}
        
    