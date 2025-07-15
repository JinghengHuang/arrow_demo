import json
from typing import List, Dict, Optional, Union
from utils.mat_parser import load_model_from_mat
from objects.lp_model import LPModel
from objects.qp_model import QPModel
from objects.solver_config import SolverConfig
import service
from service.service_factory import ServiceFactory
import pyarrow as pa

"""
Endpoints of all the exposed APIs, in logical layer
gRPC and potentially HTTP services all calls these to reduce duplication of efforts
"""
class Endpoint:
    def __init__(self):
        self.service_factory = ServiceFactory()
        pass
    def get_model_list(self, page: int = 0, result_per_page: int = 10) -> List[Dict]:
        """
        Retrieve a paginated list of saved models.

        :param page: Page number (default: 0)
        :param result_per_page: Number of models per page (default: 10)
        :return: List of model metadata
        """
        pass

    def get_recent_data_list(self) -> List[Dict]:
        """
        Retrieve a short list of recent cached data.

        :return: List of recent data metadata
        """
        pass

    def save_model(self, payload: Dict) -> Dict:
        """
        Save a new model or update an existing one.

        :param payload: Dict with fields `modelId`, `modelName`, `model`
        :return: Dict with saved model ID and status message
        """
        pass

    def delete_model(self, model_id: str) -> Dict:
        """
        Soft delete a model by model ID.

        :param model_id: The model ID to delete
        :return: Dict with deletion status message
        """
        pass

    def compute(self, payload) -> Dict:
        """
        Execute computation using a model and data, either from ID or inline.

        :param payload: Dict with fields:
            - modelId or model
            - dataId or data
            - dataName (optional)
        :return: Dict with result metadata and output
        """
        try:    
            model_name = payload.column("model_name")[0].as_py()
            engine = payload.column("engine")[0].as_py()
            service = self.service_factory.create_service(engine)
            # Note: solver is a dictionary, we can access its fields directly
            solver = SolverConfig.from_dict(payload.column("solver")[0].as_py())
            #use case when for solver_type to form model
            model = None
            if solver.solver_type.lower() == "lp":
                model = LPModel.from_dict(payload.column("model")[0].as_py())
            elif solver.solver_type.lower() == "qp":
                model = QPModel.from_dict(payload.column("model")[0].as_py())
            result = service.compute(model, solver)
            if result.column("success")[0].as_py():
                return True, pa.RecordBatch.from_pydict({
                    "solution": [result.column("solution")[0].as_py()],
                    "objective_value": [result.column("objective_value")[0].as_py()],
                })
            return False, pa.RecordBatch.from_pydict({
                    "error_code": [500],
                    "error_message": [result.column("error_message")[0].as_py()]
                })
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error in compute: {e}")
            return False, pa.RecordBatch.from_pydict(
                {
                    "error_code": [400],
                    "error_message": [f'{type(e).__name__}: {str(e)}']
                }
            )

    def compute_cobra(self, payload: Dict) -> Dict:
        """
        Execute a computation using a COBRA model, cached temporarily.

        :param payload: Dict with COBRA model JSON
        :return: Dict with result metadata and output
        """
        pass
    
    def parse_model(self, payload) -> Dict:
        """
        Parse a model from a file-like object.

        :param payload: Dict with fields:
            - modelId
            - modelName
            - model (file-like object)
        :return: Dict with parsed model metadata
        """
        return {"engine_model": load_model_from_mat(payload)}
        # pass