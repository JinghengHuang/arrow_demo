"""
Endpoints for the optimization service API
"""
from typing import Dict
import pyarrow as pa
from objects.model_factory import ModelFactory
from service.service_factory import ServiceFactory
from utils.dict_to_pa_table import dict_to_pa_table


class Endpoint:
    """
    Endpoint class for handling optimization service requests
    This class provides methods to handle various endpoints for the optimization service,
    including model management and computation requests.
    It uses a service factory to create service instances based on the engine type.
    It defines methods for getting model lists, saving models, deleting models,
    and executing computations.
    It also provides methods for parsing models and executing computations using the appropriate service.
    It is designed to be used with a web framework like FastAPI to handle HTTP requests.
    It uses the ServiceFactory to create service instances based on the engine type.
    It provides methods to handle model management and computation requests.
    It defines methods for getting model lists, saving models, deleting models,
    and executing computations.
    """
    def __init__(self):
        self.service_factory = ServiceFactory()
        self.model_factory = ModelFactory()


    def compute(self, payload) -> Dict:
        """
        Execute computation using a model and data, either from ID or inline.

        Args:
            payload (Dict): with fields:
            - model_name: str, name of model
            - model: Dict, model configuration
            - solver: Dict, solver configuration

        Returns:
            Dict: result metadata and output
        """
        engine = payload.column("engine")[0].as_py()
        optimization_service = self.service_factory.create_service(engine)
        solver_model = self.model_factory.create_model("solver", payload.column("solver")[0].as_py())
        model_name = payload.column("model_name")[0].as_py()
        data_model = self.model_factory.create_model(
            solver_model.solver_type.lower(),
            payload.column("model")[0].as_py()
        )
        result = optimization_service.compute(data_model, solver_model, model_name)
        if result.column("success")[0].as_py():
            return True, result
        return False, pa.RecordBatch.from_pydict({
                "error_message": [result.column("error_message")[0].as_py()]
            })
