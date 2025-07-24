"""
    class SolverConfig:
    This class is used to store the configuration for the solver.
    It includes the solver name, the solver type, and any additional parameters needed for the solver
"""
from service.model_service.base_model import ArrowModel


class SolverModel(ArrowModel):
    """
    SolverModel: Configuration for the optimization solver
    This class provides a way to define the solver configuration, including the solver name,
    solver type, and any additional parameters needed for the solver.
    It inherits from ArrowModel to ensure compatibility with Arrow's in-memory format.
    It provides methods to convert the configuration to a dictionary representation
    and perform consistency checks.
    """
    def __init__(self, solver_dict: dict):
        """
        Initialize the SolverConfig with the solver name, type, and parameters.
        
        :param solver_name: Name of the solver (e.g., "Highs", "GLPK", etc.)
        :param solver_type: Type of the solver (e.g., "LP", "MILP", etc.)
        :param params: Additional parameters for the solver, if any

        Args:
            solver_dict (dict): solver configuration dict, params include:
                solver_name: Name of the solver (e.g., "Highs", "GLPK", etc.)
                solver_type: Type of the solver (e.g., "LP", "MILP", etc.)

        Raises:
            ValueError: handles wrongful input, such as empty solver name or unsupported solver type.
        """
        solver_name = solver_dict.get("solver_name")
        solver_type = solver_dict.get("solver_type")
        solver_params = solver_dict.get("solver_params", {})

        self.solver_name = solver_name
        if not solver_name:
            raise ValueError("Solver name cannot be empty.")
        self.solver_type = solver_type
        if solver_type is None or solver_type.upper() not in ["LP", "QP"]:
            raise ValueError(f"Unsupported solver type: {solver_type}. Supported types are: LP, QP.")
        self.solver_params = solver_params if solver_params is not None else {}

    def sanity_check(self) -> None:
        pass
