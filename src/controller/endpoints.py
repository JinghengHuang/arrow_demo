"""
Endpoints for the optimization service API
"""
from typing import Dict
import pyarrow as pa
from src.objects.lp_model import LPModel
from src.objects.qp_model import QPModel
from src.objects.solver_config import SolverConfig
from src.service.service_factory import ServiceFactory


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


    def compute(self, payload) -> Dict:
        """
        Execute computation using a model and data, either from ID or inline.

        :param payload: Dict with fields:
            - modelId or model
            - dataId or data
            - dataName (optional)
        :return: Dict with result metadata and output
        """
        engine = payload.column("engine")[0].as_py()
        optimization_service = self.service_factory.create_service(engine)
        # Note: solver is a dictionary, we can access its fields directly
        solver = SolverConfig(payload.column("solver")[0].as_py())
        #use case when for solver_type to form model
        model_name = payload.column("model_name")[0].as_py()
        model = None
        if solver.solver_type.lower() == "lp":
            model = LPModel(payload.column("model")[0].as_py())
        elif solver.solver_type.lower() == "qp":
            model = QPModel(payload.column("model")[0].as_py())
        result = optimization_service.compute(model, solver, model_name)
        if result.column("success")[0].as_py():
            return True, pa.RecordBatch.from_pydict({
                "solution": [result.column("solution")[0].as_py()],
                "objective_value": [result.column("obj_val")[0].as_py()],
            })
        return False, pa.RecordBatch.from_pydict({
                "error_message": [result.column("error_message")[0].as_py()]
            })
