"""
Base solver class for optimization problems using Pyomo
"""
# Base class for all solvers
class BaseSolver:
    """Base class for all solvers, providing a common interface."""
    def __init__(self):
        pass

    # Generalized, use a dict (from a json)
    def run(self, params:dict) -> dict:
        """Run solver based on dict parameter

        Args:
            params (dict): model parameter

        Returns:
            dict: results
        """
        raise NotImplementedError("This method should be overridden by subclasses")
