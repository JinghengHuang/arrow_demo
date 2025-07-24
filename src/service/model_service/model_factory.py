"""
Model factory for creating optimization models
"""
from service.model_service.lp_model import LPModel
from service.model_service.qp_model import QPModel
from service.model_service.solver_model import SolverModel

class ModelFactory:
    _registry = {
        "lp": LPModel,
        "qp": QPModel,
        "solver": SolverModel,
    }

    @classmethod
    def create_model(cls, model_type: str, data):
        """
        Create an optimization model instance based on the specified type.

        Args:
            model_type (str): The type of model to create ('lp', 'qp', 'solver').
            data: The data required to initialize the model.

        Returns:
            An instance of the specified model type.

        Raises:
            ValueError: If the model type is not supported.
        """
        model_cls = cls._registry.get(model_type.lower())
        if not model_cls:
            raise ValueError(f"Unsupported model type: {model_type}")
        return model_cls(data)
