# Base solver
import pyarrow as pa

# Base class for all solvers
class BaseSolver:
    def __init__(self):
        pass

    def run(self, params:pa.Table) -> pa.Table:
        """Run solver based on ArrowTable parameter

        Args:
            params (pa.Table): model parameter

        Returns:
            pa.Table: results
        """
        pass
    # Generalized, use a dict (from a json)
    def run(self, params:dict) -> dict:
        
        """Run solver based on dict parameter

        Args:
            params (dict): model parameter

        Returns:
            dict: results
        """
        pass