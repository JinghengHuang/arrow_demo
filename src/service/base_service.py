"""
Base class for all services
"""

class BaseService():
    """
    BaseService: A base class for all services
    This class provides a common interface for services that can be extended
    to implement specific functionality.
    It defines a compute method that should be implemented by subclasses.
    """
    def __init__(self):
        pass

    def compute(self, model, solver, model_name=None):
        """Run compute service, returns result of computation
            
        :param model: The model to compute
        :param solver: The solver configuration to use
        :param model_name: Optional name for the model
        :return: Result of the computation as a PyArrow Table
        :raises NotImplementedError: If the method is not implemented in the subclass
        """
        raise NotImplementedError("Subclasses must implement compute method")
