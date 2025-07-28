"""
Base class for all services
"""

class BaseOptService():
    """
    BaseOptService: A base class for all optimization services
    This class provides a common interface for services that can be extended
    to implement specific functionality.
    It defines a compute method that should be implemented by subclasses.
    """
    def __init__(self):
        pass

    def compute(self, model, solver, model_name=None):
        """Run compute service, returns result of computation
            

        Args:
            model (dict): The model to compute
            solver (dict): The solver configuration to use
            model_name (str, optional): Optional name for the model. Defaults to None.
        Returns:
            pa.Table: Result of the computation as a PyArrow Table
        Raises:
            NotImplementedError: If the method is not implemented in the subclass
        """
        raise NotImplementedError("Subclasses must implement compute method")
